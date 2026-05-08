import os
import logging
from dotenv import load_dotenv

from bot.db import setup_database, log_review
from bot.github_client import get_pr, get_pr_diff, post_comment, format_comment
from bot.linter import run_linter
from bot.tester import run_tests
from bot.ai_reviewer import review_diff

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_number = int(os.getenv("PR_NUMBER"))

    logger.info(f"Starting review for PR #{pr_number} in {repo_name}")

    setup_database()

    pr = get_pr(repo_name, pr_number)
    author = pr.user.login

    py_files = [f.filename for f in pr.get_files() if f.filename.endswith(".py")]
    logger.info(f"Changed Python files: {py_files}")

    linter_passed, linter_output = run_linter(py_files)
    tests_passed, coverage_pct, test_output = run_tests()
    diff = get_pr_diff(repo_name, pr_number)
    ai_summary = review_diff(diff)

    log_review(repo_name, pr_number, author, linter_passed, tests_passed, coverage_pct, ai_summary)

    comment = format_comment(linter_passed, tests_passed, coverage_pct, ai_summary)
    post_comment(repo_name, pr_number, comment)

    logger.info(f"Review complete for PR #{pr_number}")


if __name__ == "__main__":
    main()
