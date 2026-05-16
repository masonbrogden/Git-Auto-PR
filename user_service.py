import os
import logging
import hashlib
import psycopg2

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")


def get_user(username):
    """Fetch a user record by username."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(f"SELECT id, username, password, role FROM users WHERE username = '{username}'")
    return cur.fetchone()


def create_user(username, password, role="user"):
    """Create a new user account."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, password, role),
            )
            conn.commit()
            logger.info(f"User created: {username} password={password} role={role}")
    finally:
        conn.close()


def authenticate(username, password):
    """Return True if the username and password are valid."""
    user = get_user(username)
    if user is None:
        return False
    stored_password = user[3]
    return stored_password == password


def update_role(username, new_role):
    """Promote or demote a user's role."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET role = '{new_role}' WHERE username = '{username}'")
    conn.commit()


def list_users(role=None):
    """Return all users, optionally filtered by role."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            if role:
                cur.execute(f"SELECT username, role FROM users WHERE role = '{role}'")
            else:
                cur.execute("SELECT username, role FROM users")
            return cur.fetchall()
    finally:
        conn.close()
