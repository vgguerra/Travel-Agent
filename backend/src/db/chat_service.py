"""
Service layer for chat session and message persistence.
Uses psycopg2 with the same connection as migrate.py.
"""

import uuid
from typing import Optional

import psycopg2
import psycopg2.extras

from src.db.migrate import _get_connection_string

MAX_HISTORY_MESSAGES = 20  # 10 exchanges


def _conn():
    return psycopg2.connect(_get_connection_string())


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

def create_session(user_id: str, title: str = "Nova conversa") -> dict:
    """Create a new chat session and return it."""
    session_id = str(uuid.uuid4())
    with _conn() as conn:
        conn.autocommit = True
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO public.chat_sessions (session_id, user_id, title)
                VALUES (%s, %s, %s)
                RETURNING session_id, user_id, title, created_at, updated_at
                """,
                (session_id, user_id, title),
            )
            return dict(cur.fetchone())


def list_sessions(user_id: str, limit: int = 50) -> list[dict]:
    """Return user's sessions ordered by most recent activity."""
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT session_id, title, created_at, updated_at
                FROM public.chat_sessions
                WHERE user_id = %s
                ORDER BY updated_at DESC
                LIMIT %s
                """,
                (user_id, limit),
            )
            return [dict(r) for r in cur.fetchall()]


def get_session(session_id: str, user_id: str) -> Optional[dict]:
    """Get a session only if it belongs to the user."""
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT session_id, title, created_at, updated_at
                FROM public.chat_sessions
                WHERE session_id = %s AND user_id = %s
                """,
                (session_id, user_id),
            )
            row = cur.fetchone()
            return dict(row) if row else None


def update_session_title(session_id: str, user_id: str, title: str) -> bool:
    """Rename a session. Returns True if updated."""
    with _conn() as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE public.chat_sessions
                SET title = %s, updated_at = now()
                WHERE session_id = %s AND user_id = %s
                """,
                (title, session_id, user_id),
            )
            return cur.rowcount > 0


def delete_session(session_id: str, user_id: str) -> bool:
    """Delete a session and cascade messages. Returns True if deleted."""
    with _conn() as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM public.chat_sessions
                WHERE session_id = %s AND user_id = %s
                """,
                (session_id, user_id),
            )
            return cur.rowcount > 0


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

def add_message(session_id: str, role: str, content: str) -> dict:
    """Insert a message into a session."""
    with _conn() as conn:
        conn.autocommit = True
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO public.chat_messages (session_id, role, content)
                VALUES (%s, %s, %s)
                RETURNING message_id, session_id, role, content, created_at
                """,
                (session_id, role, content),
            )
            return dict(cur.fetchone())


def get_messages(session_id: str) -> list[dict]:
    """Return all messages for a session in chronological order."""
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT message_id, role, content, created_at
                FROM public.chat_messages
                WHERE session_id = %s
                ORDER BY created_at ASC
                """,
                (session_id,),
            )
            return [dict(r) for r in cur.fetchall()]


def get_history_for_llm(session_id: str) -> list[dict]:
    """Return recent messages formatted for the LLM (role + content only)."""
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT role, content
                FROM public.chat_messages
                WHERE session_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (session_id, MAX_HISTORY_MESSAGES),
            )
            rows = [dict(r) for r in cur.fetchall()]
            rows.reverse()  # chronological order
            return rows
