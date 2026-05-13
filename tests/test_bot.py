from unittest.mock import patch, MagicMock

from bot.linter import run_linter
from bot.tester import run_tests, _parse_coverage, _parse_coverage_breakdown
from bot.github_client import format_comment
from bot.db import setup_database, log_review


# --- linter ---

def test_run_linter_no_files():
    passed, output = run_linter([])
    assert passed is True
    assert "No Python files" in output


def test_run_linter_passes():
    mock_result = MagicMock(returncode=0, stdout="", stderr="")
    with patch("bot.linter.subprocess.run", return_value=mock_result):
        passed, output = run_linter(["bot/main.py"])
    assert passed is True


def test_run_linter_fails():
    mock_result = MagicMock(
        returncode=1,
        stdout="bot/main.py:1:1: E302 expected 2 blank lines\n",
        stderr="",
    )
    with patch("bot.linter.subprocess.run", return_value=mock_result):
        passed, output = run_linter(["bot/main.py"])
    assert passed is False
    assert "E302" in output


# --- tester ---

def test_parse_coverage_found():
    output = "TOTAL                    100     20    80%\n"
    assert _parse_coverage(output) == 80.0


def test_parse_coverage_not_found():
    assert _parse_coverage("no coverage info here") == 0.0


def test_run_tests_passes():
    mock_result = MagicMock(returncode=0, stdout="TOTAL    100    0   100%", stderr="")
    with patch("bot.tester.subprocess.run", return_value=mock_result):
        passed, coverage, output, breakdown = run_tests()
    assert passed is True
    assert coverage == 100.0


def test_run_tests_fails():
    mock_result = MagicMock(
        returncode=1,
        stdout="TOTAL    100    50   50%\n1 failed",
        stderr="",
    )
    with patch("bot.tester.subprocess.run", return_value=mock_result):
        passed, coverage, output, breakdown = run_tests()
    assert passed is False
    assert coverage == 50.0


def test_parse_coverage_breakdown():
    output = (
        "bot/ai_reviewer.py    20     2    90%   32, 45\n"
        "bot/db.py             35     0   100%\n"
        "bot/main.py           25     5    80%   38-42\n"
    )
    rows = _parse_coverage_breakdown(output)
    assert len(rows) == 3
    assert rows[0] == {"file": "bot/ai_reviewer.py", "stmts": 20, "miss": 2, "cover": 90, "missing": "32, 45"}
    assert rows[1]["missing"] == ""
    assert rows[2]["cover"] == 80


# --- github_client ---

def test_format_comment_all_passed():
    comment = format_comment(True, True, 85.5, "Looks great!")
    assert "✅ Passed" in comment
    assert "85.5%" in comment
    assert "Looks great!" in comment


def test_format_comment_linter_failed():
    comment = format_comment(False, True, 70.0, "Some issues found")
    assert comment.count("❌ Failed") == 1
    assert comment.count("✅ Passed") == 1


def test_format_comment_all_failed():
    comment = format_comment(False, False, 0.0, "Major issues")
    assert comment.count("❌ Failed") == 2


# --- db ---

def _make_mock_conn():
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return mock_conn, mock_cursor


def test_setup_database():
    mock_conn, mock_cursor = _make_mock_conn()
    with patch("bot.db.get_connection", return_value=mock_conn):
        setup_database()
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


def test_log_review():
    mock_conn, mock_cursor = _make_mock_conn()
    with patch("bot.db.get_connection", return_value=mock_conn):
        log_review("owner/repo", 42, "alice", True, True, 90.0, "Great PR!")
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()
