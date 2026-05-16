from unittest.mock import patch, MagicMock
from user_service import list_users, update_role


def _mock_conn(rows):
    cur = MagicMock()
    cur.fetchall.return_value = rows
    conn = MagicMock()
    conn.cursor.return_value.__enter__ = MagicMock(return_value=cur)
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return conn, cur


def test_list_users_no_filter():
    conn, cur = _mock_conn([("alice", "admin"), ("bob", "user")])
    with patch("user_service.psycopg2.connect", return_value=conn):
        result = list_users()
    assert len(result) == 2


def test_list_users_with_role():
    conn, cur = _mock_conn([("alice", "admin")])
    with patch("user_service.psycopg2.connect", return_value=conn):
        result = list_users(role="admin")
    assert result[0][1] == "admin"


def test_update_role():
    conn = MagicMock()
    conn.cursor.return_value = MagicMock()
    with patch("user_service.psycopg2.connect", return_value=conn):
        update_role("alice", "admin")
    conn.commit.assert_called_once()
