import sqlite3
import asyncio
import os
from typing import List, Dict, Any
from src.config.settings import SQLITE_DB_PATH
from src.core.logger import get_logger

logger = get_logger(__name__)


def _get_connection() -> sqlite3.Connection:
    """Creates a new sqlite3 connection with Row factory."""
    # Ensure directory exists if DB path includes folders
    db_dir = os.path.dirname(SQLITE_DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the SQLite database and ensures required tables and indices exist."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_chat_history_session_id 
                ON chat_history(session_id);
                """
            )
            conn.commit()
            logger.info(f"SQLite database initialized at: {SQLITE_DB_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize SQLite database: {e}")
        raise e


def _sync_insert_message(session_id: str, role: str, content: str):
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO chat_history (session_id, role, content)
            VALUES (?, ?, ?);
            """,
            (session_id, role, content),
        )
        conn.commit()


def _sync_get_history(session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT session_id, role, content, created_at
            FROM chat_history
            WHERE session_id = ?
            ORDER BY id ASC
            LIMIT ?;
            """,
            (session_id, limit),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


async def insert_message(session_id: str, role: str, content: str):
    """Asynchronously inserts a chat message into SQLite."""
    await asyncio.to_thread(_sync_insert_message, session_id, role, content)


async def fetch_history(session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Asynchronously retrieves chat history from SQLite for a session."""
    return await asyncio.to_thread(_sync_get_history, session_id, limit)


# Initialize DB on module import
try:
    init_db()
except Exception as e:
    logger.error(f"SQLite setup warning: {e}")
