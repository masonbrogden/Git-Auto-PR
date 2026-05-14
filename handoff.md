# Handoff — Git-Auto-PR

## Goal
Build a GitHub PR Review Bot as a portfolio project. When a PR is opened or updated, GitHub
Actions triggers a workflow that builds a Docker container, runs automated checks on the PR
code, and posts a formatted review comment directly on the PR.

Stretch goals (all implemented, last one not yet verified end-to-end):
1. Slack notification when bot fails — done
2. React + Recharts dashboard showing review history — built locally, not yet deployed
3. AI review quality that cites specific line numbers like a senior engineer — in progress

---

## Current State

The pipeline works end-to-end EXCEPT the AI review step is broken due to a bad secret.
Everything up to review_diff() runs fine, then fails.

Working: PR opened → GitHub Actions → Docker build → flake8 linter → pytest + coverage → Postgres log
Broken: ANTHROPIC_API_KEY was saved in GitHub Secrets with a trailing newline character.

The exact error is:
  httpcore.LocalProtocolError: Illegal header value b'***\n'

The \n after *** (the masked secret) is the literal newline stored in the secret.
HTTP headers cannot contain newlines, so the SDK rejects the request before it leaves the container.

WHAT TO DO FIRST NEXT SESSION:
  1. GitHub repo → Settings → Secrets and variables → Actions
  2. Delete ANTHROPIC_API_KEY
  3. Re-add it, pasting the key with no trailing newline
  4. Then retrigger:
       git commit --allow-empty -m "Retrigger after ANTHROPIC_API_KEY secret fix"
       git push origin PR-test

---

## Branch State
- PR-test  — active working branch, all recent changes here, PR #1 is the live test PR
- main     — last stable state (OpenAI-based bot, before Claude migration)
- All changes in the table below are on PR-test and NOT yet merged to main

---

## What Was Changed This Session

| File | Change |
|------|--------|
| bot/ai_reviewer.py | Switched from OpenAI (gpt-4o-mini) to Anthropic SDK (claude-sonnet-4-6). Rewrote prompts to be strict and diff-specific. |
| bot/tester.py | Added _parse_coverage_breakdown() for per-file coverage rows. run_tests() now returns a 4-tuple: (tests_passed, coverage_pct, output, breakdown). |
| bot/github_client.py | Added _number_patch_lines() to prefix every diff line with its new-file line number. Updated format_comment() to accept and render a Coverage Breakdown table. |
| bot/main.py | Unpacks 4-tuple from run_tests(), passes coverage_breakdown to format_comment(). |
| tests/test_bot.py | Updated two tests to unpack 4-tuple. Added test_parse_coverage_breakdown(). Imported _parse_coverage_breakdown. |
| .github/workflows/review.yml | Removed debug "Check secrets" step. Added Slack failure notification (if: failure()). Swapped OPENAI_API_KEY for ANTHROPIC_API_KEY. |
| Dockerfile | Added apt-get install ca-certificates before pip install (needed for SSL in slim image). |
| api/main.py | New FastAPI service: GET /reviews returns all Postgres rows, GET /health for uptime checks. |
| api/requirements.txt | fastapi, uvicorn, psycopg2-binary |
| api/Dockerfile | python:3.12-slim, runs uvicorn on port 8000 |
| dashboard/ | Full React + Vite + Recharts app. Dark theme. Stat cards, area chart (coverage over time), bar chart (pass/fail counts), review history table. |
| dashboard/Dockerfile | Multi-stage: node build → nginx. entrypoint.sh injects window.API_URL at container start so the URL is configurable without rebuilding the image. |
| docker-compose.yml | Added api (port 8000) and dashboard (port 3000) services. |

---

## Files Actively Being Worked On
- .github/workflows/review.yml — Slack step still failing (see below)
- bot/ai_reviewer.py — code is correct, blocked only by the bad secret

---

## What Was Tried and Failed

### 1. Passing secrets inline in docker run command
  FAILED:  -e OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}
GitHub Actions does not interpolate secrets inside multiline run: shell commands.
  FIX: Declare at the step env: level and pass by name: -e OPENAI_API_KEY

### 2. ANTHROPIC_API_KEY saved with trailing newline — CURRENT BLOCKER
  ERROR: httpcore.LocalProtocolError: Illegal header value b'***\n'
The \n is a literal newline stored as part of the secret when pasted into GitHub.
  FIX: Delete and re-add the secret with no trailing newline (see top of this file).

### 3. npm ci failed in dashboard Docker build
npm ci requires a package-lock.json which did not exist yet.
  FIX: Temporarily swapped to npm install, ran it locally, committed package-lock.json,
       switched back to npm ci.

### 4. Anthropic SSL connection error (before ca-certificates fix)
python:3.12-slim was missing ca-certificates, causing SSL failures to api.anthropic.com.
  FIX: Added apt-get install -y ca-certificates to Dockerfile before pip install.

### 5. AI review was generic even after prompt rewrite
The AI cited no line numbers and returned None for all issues. Two root causes:
  - gpt-4o-mini is too weak for line-specific analysis
  - The diff had no line numbers so the model had nothing to cite
  FIX: Switched to claude-sonnet-4-6 AND added _number_patch_lines() to number every
       diff line. Not yet verified end-to-end because of the secret bug.

### 6. Slack notification failing (curl exit code 3, URL malformed)
Exit code 3 from curl means the URL string is empty. The SLACK_WEBHOOK_URL secret may have
a name mismatch or trailing newline. The webhook URL itself is valid (tested manually).
  INVESTIGATE: After fixing ANTHROPIC_API_KEY. If the bot succeeds, this step won't fire
               anyway. If it still fails, delete and re-add SLACK_WEBHOOK_URL cleanly.

---

## Environment Notes
- ANTHROPIC_API_KEY  — GitHub Secrets (broken, trailing newline) AND local .env
- OPENAI_API_KEY     — GitHub Secrets AND local .env (kept as fallback, not used in code)
- GITHUB_TOKEN       — GitHub Secrets AND local .env
- SLACK_WEBHOOK_URL  — GitHub Secrets (may need re-adding)
- DATABASE_URL       — hardcoded in workflow: postgresql://prbot:prbot123@localhost:5432/prbot_db
- Local .env is gitignored, never committed
- PR-test is the test branch — PR #1 is the live test PR

---

## Next Steps (in order)

1. Fix ANTHROPIC_API_KEY secret (see top — delete and re-add with no trailing newline)
2. Verify Claude review quality — confirm the comment cites specific line numbers and gives a real verdict
3. Fix Slack notification if still failing after step 1
4. Merge PR-test to main once the full pipeline is green
5. Deploy to Railway:
     - Push main to GitHub
     - railway.app → New Project → Deploy from GitHub
     - Add Postgres plugin
     - api service: Root Directory = api/, DATABASE_URL = Railway Postgres URL
     - dashboard service: Root Directory = dashboard/, API_URL = public URL of the api service
6. Clean up — remove OPENAI_API_KEY from secrets and .env once Claude is confirmed working
