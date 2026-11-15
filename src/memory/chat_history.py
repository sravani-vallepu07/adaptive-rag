from typing import List, Dict, Any
from src.db.sqlite_client import insert_message, fetch_history
from src.core.logger import get_logger

logger = get_logger(__name__)


async def save_message(session_id: str, role: str, content: str):
    """Saves a user or assistant message to the SQLite chat history."""
    try:
        await insert_message(session_id, role, content)
    except Exception as e:
        logger.error(f"Failed to save message to SQLite: {e}")


async def get_history(session_id: str) -> List[Dict[str, Any]]:
    """Retrieves chat history for a session from SQLite."""
    try:
        return await fetch_history(session_id)
    except Exception as e:
        logger.error(f"Failed to get history from SQLite: {e}")
        return []
