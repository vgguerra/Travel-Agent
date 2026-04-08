"""
Service layer for profile queries (username check, email resolution).
"""

from typing import Optional

import psycopg2.extras

from src.db.migrate import _get_connection_string


def _conn():
    return psycopg2.connect(_get_connection_string())


def username_exists(username: str) -> bool:
    """Check if a username is already taken."""
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM public.profiles WHERE username = %s LIMIT 1",
                (username.lower(),),
            )
            return cur.fetchone() is not None


def get_email_by_username(username: str) -> Optional[str]:
    """Resolve a username to its email. Returns None if not found."""
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT email FROM public.profiles WHERE username = %s",
                (username.lower(),),
            )
            row = cur.fetchone()
            return row["email"] if row else None
