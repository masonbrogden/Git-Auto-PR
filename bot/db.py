import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_connection():
    """Create and return a connection to the Postgres database."""
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        logger.info("Database connection established")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def setup_database():
    """Create the reviews table if it doesn't exist."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id              SERIAL PRIMARY KEY,
                    repo            VARCHAR(255),
                    pr_number       INTEGER,
                    author          VARCHAR(255),
                    linter_passed   BOOLEAN,
                    tests_passed    BOOLEAN,
                    coverage_pct    FLOAT,
                    ai_summary      TEXT,
                    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            logger.info("Database setup complete")
    except Exception as e:
        logger.error(f"Failed to setup database: {e}")
        raise
    finally:
        conn.close()

def log_review(repo, pr_number, author, linter_passed, tests_passed, coverage_pct, ai_summary):
    """Insert a review record into the database."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO reviews 
                    (repo, pr_number, author, linter_passed, tests_passed, coverage_pct, ai_summary)
                VALUES 
                    (%s, %s, %s, %s, %s, %s, %s)
            """, (repo, pr_number, author, linter_passed, tests_passed, coverage_pct, ai_summary))
            conn.commit()
            logger.info(f"Review logged for PR #{pr_number} in {repo}")
    except Exception as e:
        logger.error(f"Failed to log review: {e}")
        raise
    finally:
        conn.close()

def get_reviews(repo=None):
    """Fetch all reviews, optionally filtered by repo."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if repo:
                cur.execute("SELECT * FROM reviews WHERE repo = %s ORDER BY created_at DESC", (repo,))
            else:
                cur.execute("SELECT * FROM reviews ORDER BY created_at DESC")
            return cur.fetchall()
    except Exception as e:
        logger.error(f"Failed to fetch reviews: {e}")
        raise
    finally:
        conn.close()