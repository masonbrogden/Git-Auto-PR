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


def _write_output(key, value):
    output_file = os.getenv("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"{key}={value}\n")


def _extract_verdict(ai_summary):
    if not ai_summary:
        return "Needs Discussion"
    for line in ai_summary.splitlines():
        if line.strip().startswith("**Verdict:**"):
            for v in ["Approve", "Request Changes", "Needs Discussion"]:
                if v in line:
                    return v
    return "Needs Discussion"


def main():
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_number = int(os.getenv("PR_NUMBER"))
    workspace = os.getenv("GITHUB_WORKSPACE", ".")

    run_linter_flag = os.getenv("RUN_LINTER", "true").lower() == "true"
    run_tests_flag = os.getenv("RUN_TESTS", "true").lower() == "true"
    coverage_threshold = float(os.getenv("COVERAGE_THRESHOLD", "0"))
    database_url = os.getenv("DATABASE_URL", "")

    logger.info(f"Starting review for PR #{pr_number} in {repo_name}")

    if database_url:
        setup_database()

    pr = get_pr(repo_name, pr_number)
    author = pr.user.login

    py_files = [f.filename for f in pr.get_files() if f.filename.endswith(".py")]
    logger.info(f"Changed Python files: {py_files}")

    linter_passed = True
    if run_linter_flag:
        linter_passed, _ = run_linter(py_files, working_dir=workspace)
    else:
        logger.info("Linter skipped (RUN_LINTER=false)")

    tests_passed = True
    coverage_pct = 0.0
    coverage_breakdown = []
    if run_tests_flag:
        tests_passed, coverage_pct, _, coverage_breakdown = run_tests(working_dir=workspace)
        if coverage_threshold > 0 and coverage_pct < coverage_threshold:
            logger.warning(f"Coverage {coverage_pct:.1f}% below threshold {coverage_threshold:.1f}%")
            tests_passed = False
    else:
        logger.info("Tests skipped (RUN_TESTS=false)")

    diff = get_pr_diff(repo_name, pr_number)
    ai_summary = review_diff(diff)

    if database_url:
        log_review(repo_name, pr_number, author, linter_passed, tests_passed, coverage_pct, ai_summary)

    comment = format_comment(linter_passed, tests_passed, coverage_pct, ai_summary, coverage_breakdown)
    post_comment(repo_name, pr_number, comment)

    verdict = _extract_verdict(ai_summary)
    _write_output("verdict", verdict)
    _write_output("coverage_pct", f"{coverage_pct:.1f}")
    _write_output("linter_passed", str(linter_passed).lower())
    _write_output("tests_passed", str(tests_passed).lower())

    logger.info(f"Review complete for PR #{pr_number}")


if __name__ == "__main__":
    main()
