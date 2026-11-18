"""Simple SQLite storage for NewsLens stories."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional


DATABASE_PATH = Path(__file__).resolve().parent / "newslens.db"


def get_connection() -> sqlite3.Connection:
    """Open a connection and return stories as dictionaries."""
    connection = sqlite3.connect(str(DATABASE_PATH))
    connection.row_factory = sqlite3.Row
    return connection


def create_table() -> None:
    """Create the stories table if it does not exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS stories (
                id TEXT PRIMARY KEY,
                title TEXT,
                summary TEXT,
                link TEXT,
                source TEXT,
                published TEXT,
                fetched_at TEXT
            )
            """
        )


def save_stories(stories: Iterable[Dict[str, str]]) -> int:
    """Save new stories and skip duplicate story IDs."""
    create_table()
    inserted = 0
    fetched_at = datetime.utcnow().isoformat(timespec="seconds")

    with get_connection() as connection:
        for story in stories:
            story_id = story.get("id")
            if not story_id:
                continue

            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO stories
                    (id, title, summary, link, source, published, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    story_id,
                    story.get("title", ""),
                    story.get("summary", ""),
                    story.get("link", ""),
                    story.get("source", ""),
                    story.get("published", ""),
                    story.get("fetched_at", fetched_at),
                ),
            )
            inserted += cursor.rowcount

    return inserted


def get_stories(limit: int = 50) -> List[Dict[str, str]]:
    """Return the newest fetched stories."""
    create_table()
    limit = max(1, limit)

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, summary, link, source, published, fetched_at
            FROM stories
            ORDER BY fetched_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_story_by_id(story_id: str) -> Optional[Dict[str, str]]:
    """Return one story by ID, or None when it does not exist."""
    create_table()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, title, summary, link, source, published, fetched_at
            FROM stories
            WHERE id = ?
            """,
            (story_id,),
        ).fetchone()

    return dict(row) if row else None


create_table()
