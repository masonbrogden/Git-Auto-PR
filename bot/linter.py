import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_linter(py_files, working_dir=None):
    """Run flake8 on the given Python files. Returns (passed, output)."""
    if not py_files:
        logger.info("No Python files to lint")
        return True, "No Python files changed."

    try:
        result = subprocess.run(
            ["flake8"] + py_files,
            capture_output=True,
            text=True,
            cwd=working_dir,
        )
        passed = result.returncode == 0
        output = result.stdout + result.stderr
        if passed:
            logger.info("Linter passed")
        else:
            logger.info(f"Linter found issues:\n{output}")
        return passed, output
    except Exception as e:
        logger.error(f"Linter failed to run: {e}")
        raise
