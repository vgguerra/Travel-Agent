"""
Supabase JWT authentication dependency for FastAPI.
Extracts and validates the Bearer token from the Authorization header,
returning the authenticated user_id (sub claim).
"""

import os

import jwt
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer()

_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")


def _verify_via_supabase_api(token: str) -> str:
    """Fallback: call Supabase /auth/v1/user to validate the token."""
    resp = requests.get(
        f"{_SUPABASE_URL}/auth/v1/user",
        headers={
            "Authorization": f"Bearer {token}",
            "apikey": os.getenv("SUPABASE_ANON_KEY", ""),
        },
        timeout=5,
    )
    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido",
        )
    return resp.json()["id"]


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> str:
    """FastAPI dependency — returns user_id (UUID string) or raises 401."""
    token = credentials.credentials

    # Prefer local JWT validation when the secret is configured
    if _JWT_SECRET:
        try:
            payload = jwt.decode(
                token,
                _JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
            )
            return payload["sub"]
        except (jwt.InvalidTokenError, KeyError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalido",
            )

    # Fallback: validate via Supabase REST API
    return _verify_via_supabase_api(token)
