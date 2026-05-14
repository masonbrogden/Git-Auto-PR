import os
from datetime import datetime
from typing import Optional

import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


class Review(BaseModel):
    id: int
    repo: Optional[str]
    pr_number: Optional[int]
    author: Optional[str]
    linter_passed: Optional[bool]
    tests_passed: Optional[bool]
    coverage_pct: Optional[float]
    ai_summary: Optional[str]
    created_at: Optional[datetime]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/reviews", response_model=list[Review])
def get_reviews():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM reviews ORDER BY created_at DESC")
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()
