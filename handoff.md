# Handoff — Git-Auto-PR

## Goal

Build Git-Auto-PR as a legitimate open source GitHub Actions Marketplace tool that any developer
can add to their repository with a single line:

```yaml
- uses: masonbrogden/git-auto-pr@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

The action runs on every pull request, performs flake8 linting, pytest with coverage, and
generates a specific line-cited AI code review using Claude — posted directly as a PR comment.

Stretch goals still remaining:
1. Marketing landing page (React, deployable to Railway or Vercel)
2. Support for non-Python repositories (language-agnostic linting/testing)
3. Move api/ and dashboard/ personal infrastructure to a separate repo

---

## Current State

**The action is published and live on the GitHub Actions Marketplace at v1.0.0.**

Pipeline works end-to-end:
- PR opened → GitHub Actions → Docker build → flake8 linter → pytest + coverage → Claude AI review → PR comment posted
- All inputs configurable: model, run_linter, run_tests, coverage_threshold, database_url
- Outputs wired to GITHUB_OUTPUT: verdict, coverage_pct, linter_passed, tests_passed
- Postgres logging is optional (skipped if DATABASE_URL is not set)
- README is written for marketplace with real screenshots of a demo review
- v1.0.0 tag points to the latest commit on main

Branch state:
- main — published, clean, everything merged here
- PR-test — deleted
- feature/user-auth — deleted (was demo branch for screenshots, never merged)

---

## Files Actively Being Worked On

None — the codebase is stable. Next session will likely start new files for the landing page.

---

## What Was Done This Session

| File | Change |
|------|--------|
| action.yml | Created from scratch — defines name, branding, inputs, outputs, runs using Docker |
| bot/main.py | Reads RUN_LINTER, RUN_TESTS, COVERAGE_THRESHOLD, DATABASE_URL, GITHUB_WORKSPACE from env. Postgres optional. Writes outputs to GITHUB_OUTPUT. Parses PR number from GITHUB_REF. |
| bot/ai_reviewer.py | Reads MODEL from env instead of hardcoding claude-sonnet-4-6 |
| bot/linter.py | Added working_dir param, passed as cwd to subprocess |
| bot/tester.py | Added working_dir param, passed as cwd to subprocess |
| bot/github_client.py | Moved import re to module level |
| Dockerfile | Changed CMD to python -m bot.main so path works from any working directory |
| requirements.txt | Removed unused openai dependency |
| .github/workflows/review.yml | Replaced manual docker build with uses: ./ to dogfood the action |
| README.md | Full rewrite for marketplace — usage, inputs, outputs, config examples, screenshots |
| handoff.md | This file |

---

## What Was Tried and Failed

### 1. github.* context in action.yml runs.env
ERROR: Unrecognized named-value: 'github'. Located at position 1 within expression: github.event.pull_request.number
In action.yml's runs.env block, only inputs.* is available — github.* context is not.
FIX: Removed PR_NUMBER from runs.env entirely. Instead parse it in main.py from GITHUB_REF
     (which GitHub sets automatically as refs/pull/{number}/merge for all PR events),
     with PR_NUMBER env var kept as a local dev fallback.

### 2. CMD with relative path broke in Docker container action
When GitHub runs a Docker container action it sets the working directory to /github/workspace
(the user's repo), not /app where the bot code lives. CMD ["python", "bot/main.py"] failed
because bot/main.py doesn't exist relative to /github/workspace.
FIX: Changed to CMD ["python", "-m", "bot.main"]. Since PYTHONPATH=/app is set in the
     Dockerfile, Python finds the module regardless of working directory.

### 3. v1.0.0 tag created before README was finalized
The tag was created pointing to an early commit before the README screenshots were added.
FIX: Deleted and recreated v1.0.0 pointing to the latest commit before publishing.
     Safe to do since the release had not yet been published to the marketplace.

---

## Environment Notes

- ANTHROPIC_API_KEY — GitHub Secrets (fixed, no trailing newline)
- GITHUB_TOKEN — automatic, provided by GitHub Actions (${{ github.token }})
- SLACK_WEBHOOK_URL — GitHub Secrets (never fully verified, only fires on failure)
- DATABASE_URL — optional, not currently set in secrets (Postgres logging disabled)
- Local .env is gitignored, never committed

---

## Next Steps (in order)

1. Build the marketing landing page
   - React app explaining what the tool does
   - Show a real screenshot of a review comment
   - Clear call to action linking to the marketplace listing
   - Deploy to Railway or Vercel
   - This is a separate repo from the action itself

2. Support non-Python repositories
   - run_linter and run_tests currently only make sense for Python
   - Could add a language input and swap linter/test commands accordingly
   - Or document clearly that linting/testing is Python-only and AI review works for any language

3. Move api/ and dashboard/ to a separate repo
   - These are personal infrastructure (FastAPI review history + React dashboard)
   - They don't belong in the action source repo — confusing to outside contributors
   - New repo name suggestion: git-auto-pr-dashboard

4. Fix Slack notification (low priority)
   - The curl step fires on failure — never triggered since the pipeline is green
   - SLACK_WEBHOOK_URL secret may have a trailing newline (same issue as the API key had)
   - Only matters if you want failure alerts

5. Tag a major version alias
   - Best practice is to also push a v1 tag that floats to the latest v1.x.x release
   - Users can then pin to @v1 and get patch updates automatically
   - Command: git tag -f v1 && git push origin v1 --force
