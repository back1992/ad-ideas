"""
Seed script for 广告思想简史 platform.

Populates the SQLite database with initial content (articles, etc.)
on first run. Idempotent — skips records that already exist.

Usage:
    python seed_db.py              # standalone
    from seed_db import seed_db    # importable
    seed_db()                      # call from app
"""

import json
import os
import sqlite3
from pathlib import Path

SEED_DIR = Path(__file__).parent / "seed_data"
DB_PATH = Path(__file__).parent / "platform.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _seed_articles(conn: sqlite3.Connection) -> int:
    """Insert articles from seed_data/articles.json. Returns count inserted."""
    articles_file = SEED_DIR / "articles.json"
    if not articles_file.exists():
        return 0

    with open(articles_file, "r", encoding="utf-8") as f:
        articles = json.load(f)

    # Normalize: the file may contain a single dict or a list
    if isinstance(articles, dict):
        articles = [articles]

    inserted = 0
    for article in articles:
        # Skip if title already exists
        existing = conn.execute(
            "SELECT id FROM articles WHERE title = ?", (article["title"],)
        ).fetchone()
        if existing:
            continue

        conn.execute(
            """INSERT INTO articles
               (title, content, excerpt, category, tags, author, status,
                created_at, updated_at, published_at, views, avg_rating, total_feedback)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                article["title"],
                article["content"],
                article.get("excerpt", ""),
                article.get("category", ""),
                article.get("tags", ""),
                article["author"],
                article.get("status", "published"),
                article.get("created_at"),
                article.get("updated_at"),
                article.get("published_at"),
                article.get("views", 0),
                article.get("avg_rating", 0.0),
                article.get("total_feedback", 0),
            ),
        )
        inserted += 1

    if inserted:
        conn.commit()
    return inserted


def seed_db() -> dict:
    """Run all seed operations. Returns a summary dict."""
    conn = _get_conn()
    try:
        # Ensure tables exist (same schema as DatabaseManager.init_database)
        from modules.database import get_database_manager

        get_database_manager().init_database()
    except Exception:
        # If import fails, tables should already exist from app startup
        pass

    summary = {}
    summary["articles"] = _seed_articles(conn)
    conn.close()
    return summary


if __name__ == "__main__":
    result = seed_db()
    print("Seed complete:", result)
