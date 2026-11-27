"""Simple SQLite storage for NewsLens stories."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Dict, Generator, Iterable, List, Optional
from zoneinfo import ZoneInfo

if __package__:
    from .story_text import clean_story_text
else:
    from story_text import clean_story_text


DATABASE_PATH = Path(__file__).resolve().parent / "newslens.db"
IST = ZoneInfo("Asia/Kolkata")


def normalize_published(value: str) -> str:
    """Convert old RSS and newer ISO timestamps to India Standard Time."""
    if not value:
        return ""

    value = value.strip()
    if not value:
        return ""

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return value

    if parsed is None:
        return value
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=IST)
    else:
        parsed = parsed.astimezone(IST)
    return parsed.isoformat(timespec="seconds")


def get_connection() -> sqlite3.Connection:
    """Open a connection and return stories as dictionaries."""
    connection = sqlite3.connect(str(DATABASE_PATH))
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def _connection_scope() -> Generator[sqlite3.Connection, None, None]:
    connection = get_connection()
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def create_table() -> None:
    """Create the stories table if it does not exist."""
    with _connection_scope() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS stories (
                id TEXT PRIMARY KEY,
                title TEXT,
                summary TEXT,
                link TEXT,
                source TEXT,
                published TEXT,
                fetched_at TEXT,
                section TEXT
            )
            """
        )
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(stories)").fetchall()
        }
        if "section" not in columns:
            connection.execute("ALTER TABLE stories ADD COLUMN section TEXT")


def migrate_published_dates() -> int:
    """Rewrite existing RSS published values to ISO 8601 in place."""
    create_table()
    migrated = 0
    with _connection_scope() as connection:
        rows = connection.execute(
            "SELECT id, published FROM stories WHERE published IS NOT NULL"
        ).fetchall()
        for row in rows:
            original = (row["published"] or "").strip()
            normalized = normalize_published(original)
            if normalized and normalized != original:
                connection.execute(
                    "UPDATE stories SET published = ? WHERE id = ?",
                    (normalized, row["id"]),
                )
                migrated += 1
    return migrated


def migrate_story_text() -> int:
    """Clean existing story titles and summaries; safe to rerun at startup."""
    create_table()
    migrated = 0
    with _connection_scope() as connection:
        rows = connection.execute(
            "SELECT id, title, summary FROM stories"
        ).fetchall()
        for row in rows:
            title = clean_story_text(row["title"])
            summary = clean_story_text(row["summary"])
            if title != row["title"] or summary != row["summary"]:
                connection.execute(
                    "UPDATE stories SET title = ?, summary = ? WHERE id = ?",
                    (title, summary, row["id"]),
                )
                migrated += 1
    return migrated


def save_stories(stories: Iterable[Dict[str, str]]) -> int:
    """Save new stories and skip duplicate story IDs."""
    create_table()
    inserted = 0
    fetched_at = datetime.utcnow().isoformat(timespec="seconds")

    with _connection_scope() as connection:
        for story in stories:
            story_id = story.get("id")
            if not story_id:
                continue

            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO stories
                    (id, title, summary, link, source, published, fetched_at, section)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    story_id,
                    story.get("title", ""),
                    story.get("summary", ""),
                    story.get("link", ""),
                    story.get("source", ""),
                    normalize_published(story.get("published", "")),
                    story.get("fetched_at", fetched_at),
                    story.get("section", "Top"),
                ),
            )
            inserted += cursor.rowcount

    return inserted


def get_stories(limit: int = 50, section: Optional[str] = None) -> List[Dict[str, str]]:
    """Return the newest fetched stories, optionally by section."""
    create_table()
    limit = max(1, limit)

    with _connection_scope() as connection:
        if section:
            rows = connection.execute(
                """
                SELECT id, title, summary, link, source, published, fetched_at, section
                FROM stories
                WHERE section = ?
                ORDER BY fetched_at DESC
                LIMIT ?
                """,
                (section, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT id, title, summary, link, source, published, fetched_at, section
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

    with _connection_scope() as connection:
        row = connection.execute(
            """
            SELECT id, title, summary, link, source, published, fetched_at, section
            FROM stories
            WHERE id = ?
            """,
            (story_id,),
        ).fetchone()

    return dict(row) if row else None
create_table()
migrate_published_dates()
