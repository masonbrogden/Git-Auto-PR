import os
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
    """Get the code diff from a pull request."""
    try:
        client = get_github_client()
        repo = client.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        files = pr.get_files()
        diff = ""
        for f in files:
            diff += f"File: {f.filename}\n"
            if f.patch:
                diff += f"{f.patch}\n"
            diff += "\n"
        logger.info(f"Fetched diff for PR #{pr_number}")
        return diff
    except Exception as e:
        logger.error(f"Failed to fetch diff for PR #{pr_number}: {e}")
        raise

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

def format_comment(linter_passed, tests_passed, coverage_pct, ai_summary):
    """Format the bot's review comment."""
    linter_status = "✅ Passed" if linter_passed else "❌ Failed"
    tests_status = "✅ Passed" if tests_passed else "❌ Failed"

    comment = f"""##  PR Review Bot Report

| Check | Status |
|-------|--------|
| Linter | {linter_status} |
| Tests | {tests_status} |
| Coverage | {coverage_pct:.1f}% |

###  AI Code Review
{ai_summary}

---
*Automated review by [Git-Auto-PR](https://github.com/masonbrogden/Git-Auto-PR)*
"""
    return comment