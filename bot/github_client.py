import os
import re
import logging
from github import Github
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_github_client():
    """Create and return an authenticated GitHub client."""
    try:
        token = os.getenv("GITHUB_TOKEN")
        client = Github(token)
        logger.info("GitHub client authenticated")
        return client
    except Exception as e:
        logger.error(f"Failed to authenticate GitHub client: {e}")
        raise

def get_pr(repo_name, pr_number):
    """Fetch a pull request object."""
    try:
        client = get_github_client()
        repo = client.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        logger.info(f"Fetched PR #{pr_number} from {repo_name}")
        return pr
    except Exception as e:
        logger.error(f"Failed to fetch PR #{pr_number}: {e}")
        raise

def get_pr_diff(repo_name, pr_number):
    """Get the code diff from a pull request with new-file line numbers."""
    try:
        client = get_github_client()
        repo = client.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        files = pr.get_files()
        diff = ""
        for f in files:
            diff += f"File: {f.filename}\n"
            if f.patch:
                diff += _number_patch_lines(f.patch) + "\n"
            diff += "\n"
        logger.info(f"Fetched diff for PR #{pr_number}")
        return diff
    except Exception as e:
        logger.error(f"Failed to fetch diff for PR #{pr_number}: {e}")
        raise


def _number_patch_lines(patch):
    """Prefix each diff line with its new-file line number."""
    result = []
    current_line = 0
    for line in patch.split("\n"):
        hunk = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
        if hunk:
            current_line = int(hunk.group(1))
            result.append(line)
        elif line.startswith("+"):
            result.append(f"{current_line:4d} {line}")
            current_line += 1
        elif line.startswith("-"):
            result.append(f"     {line}")
        else:
            result.append(f"{current_line:4d} {line}")
            current_line += 1
    return "\n".join(result)

def post_comment(repo_name, pr_number, comment):
    """Post a comment on a pull request."""
    try:
        client = get_github_client()
        repo = client.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        pr.create_issue_comment(comment)
        logger.info(f"Comment posted on PR #{pr_number}")
    except Exception as e:
        logger.error(f"Failed to post comment on PR #{pr_number}: {e}")
        raise

def format_comment(linter_passed, tests_passed, coverage_pct, ai_summary, coverage_breakdown=None):
    """Format the bot's review comment."""
    linter_status = "✅ Passed" if linter_passed else "❌ Failed"
    tests_status = "✅ Passed" if tests_passed else "❌ Failed"

    breakdown_section = ""
    if coverage_breakdown:
        rows = "\n".join(
            f"| `{r['file']}` | {r['stmts']} | {r['miss']} | {r['cover']}% | "
            f"{r['missing'] if r['missing'] else '—'} |"
            for r in coverage_breakdown
        )
        breakdown_section = f"""
### Coverage Breakdown

| File | Stmts | Miss | Cover | Missing Lines |
|------|-------|------|-------|---------------|
{rows}
"""

    comment = f"""## PR Review Bot Report

| Check | Status |
|-------|--------|
| Linter | {linter_status} |
| Tests | {tests_status} |
| Coverage | {coverage_pct:.1f}% |
{breakdown_section}
### AI Code Review
{ai_summary}

---
*Automated review by [Git-Auto-PR](https://github.com/masonbrogden/Git-Auto-PR)*
"""
    return comment