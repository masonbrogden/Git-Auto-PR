import subprocess
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_tests():
    """Run pytest with coverage. Returns (tests_passed, coverage_pct, output)."""
    try:
        result = subprocess.run(
            ["pytest", "--cov=.", "--cov-report=term-missing", "-v"],
            capture_output=True,
            text=True,
        )
        output = result.stdout + result.stderr
        tests_passed = result.returncode == 0
        coverage_pct = _parse_coverage(output)

        if tests_passed:
            logger.info(f"Tests passed. Coverage: {coverage_pct:.1f}%")
        else:
            logger.info(f"Tests failed. Coverage: {coverage_pct:.1f}%")

        return tests_passed, coverage_pct, output
    except Exception as e:
        logger.error(f"Failed to run tests: {e}")
        raise


def _parse_coverage(output):
    """Extract overall coverage percentage from pytest-cov output."""
    match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
    if match:
        return float(match.group(1))
    return 0.0
