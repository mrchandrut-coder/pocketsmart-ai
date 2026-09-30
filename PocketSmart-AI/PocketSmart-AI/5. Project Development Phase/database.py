import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATABASE_PATH = Path(
    os.getenv("DATABASE_PATH", str(Path(__file__).with_name("pocketsmart.sqlite3")))
)


def connect() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def database_connection():
    connection = connect()
    try:
        yield connection
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database() -> None:
    with database_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                email TEXT COLLATE NOCASE UNIQUE,
                full_name TEXT,
                hashed_password TEXT NOT NULL,
                disabled INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS recommendations (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                category TEXT NOT NULL,
                budget REAL NOT NULL,
                preferences TEXT NOT NULL,
                result TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS recommendations_user_time
                ON recommendations(user_id, timestamp DESC);
            """
        )


def create_user(
    username: str,
    email: str | None,
    full_name: str | None,
    hashed_password: str,
) -> int:
    with database_connection() as connection:
        cursor = connection.execute(
            """INSERT INTO users (username, email, full_name, hashed_password, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                username,
                email or None,
                full_name or None,
                hashed_password,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        return int(cursor.lastrowid)


def get_user_by_username(username: str) -> dict[str, Any] | None:
    with database_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    with database_connection() as connection:
        row = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def save_recommendation(
    recommendation_id: str,
    user_id: int,
    category: str,
    budget: float,
    preferences: dict[str, Any],
    result: str,
    timestamp: str,
) -> None:
    with database_connection() as connection:
        connection.execute(
            """INSERT INTO recommendations
               (id, user_id, category, budget, preferences, result, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                recommendation_id,
                user_id,
                category,
                budget,
                json.dumps(preferences, ensure_ascii=False),
                result,
                timestamp,
            ),
        )


def list_recommendations(user_id: int) -> list[dict[str, Any]]:
    with database_connection() as connection:
        rows = connection.execute(
            """SELECT id, category, budget, preferences, result, timestamp
               FROM recommendations WHERE user_id = ?
               ORDER BY timestamp DESC, rowid DESC""",
            (user_id,),
        ).fetchall()
    entries = []
    for row in rows:
        entry = dict(row)
        entry["preferences"] = json.loads(entry["preferences"])
        entries.append(entry)
    return entries


def clear_recommendations(user_id: int) -> int:
    with database_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM recommendations WHERE user_id = ?", (user_id,)
        )
        return cursor.rowcount
