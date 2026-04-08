"""
Supabase authentication: JWT validation dependency + auth proxy endpoints.
All Supabase interaction is server-side — the frontend never needs Supabase keys.
"""

import os

import jwt
import requests as http_client
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from src.db import profile_service

load_dotenv()

_bearer = HTTPBearer()


def _supabase_url() -> str:
    return os.getenv("SUPABASE_URL", "")


def _anon_key() -> str:
    return os.getenv("SUPABASE_ANON_KEY", "")


def _jwt_secret() -> str:
    return os.getenv("SUPABASE_JWT_SECRET", "")


def _auth_headers() -> dict:
    return {
        "apikey": _anon_key(),
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------------------------
# JWT validation dependency
# ---------------------------------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> str:
    """FastAPI dependency — returns user_id (UUID string) or raises 401."""
    token = credentials.credentials

    if _jwt_secret():
        try:
            payload = jwt.decode(
                token,
                _jwt_secret(),
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
    resp = http_client.get(
        f"{_supabase_url()}/auth/v1/user",
        headers={**_auth_headers(), "Authorization": f"Bearer {token}"},
        timeout=5,
    )
    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido",
        )
    return resp.json()["id"]


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class SignUpRequest(BaseModel):
    email: str
    password: str
    name: str
    username: str


class SignInRequest(BaseModel):
    identifier: str  # email or username
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    user: dict


# ---------------------------------------------------------------------------
# Auth proxy helpers
# ---------------------------------------------------------------------------

def _supabase_signup(email: str, password: str, name: str, username: str) -> dict:
    resp = http_client.post(
        f"{_supabase_url()}/auth/v1/signup",
        headers=_auth_headers(),
        json={
            "email": email,
            "password": password,
            "data": {"name": name, "username": username.lower()},
        },
        timeout=10,
    )
    body = resp.json()
    if resp.status_code >= 400:
        msg = body.get("msg") or body.get("message") or body.get("error_description") or str(body)
        raise HTTPException(status_code=resp.status_code, detail=msg)
    return body


def _supabase_signin(email: str, password: str) -> dict:
    resp = http_client.post(
        f"{_supabase_url()}/auth/v1/token?grant_type=password",
        headers=_auth_headers(),
        json={"email": email, "password": password},
        timeout=10,
    )
    body = resp.json()
    if resp.status_code >= 400:
        msg = body.get("msg") or body.get("message") or body.get("error_description") or str(body)
        raise HTTPException(status_code=resp.status_code, detail=msg)
    return body


def _supabase_refresh(refresh_token: str) -> dict:
    resp = http_client.post(
        f"{_supabase_url()}/auth/v1/token?grant_type=refresh_token",
        headers=_auth_headers(),
        json={"refresh_token": refresh_token},
        timeout=10,
    )
    body = resp.json()
    if resp.status_code >= 400:
        msg = body.get("msg") or body.get("message") or body.get("error_description") or str(body)
        raise HTTPException(status_code=resp.status_code, detail=msg)
    return body


# ---------------------------------------------------------------------------
# Auth endpoints (to be mounted on the FastAPI app)
# ---------------------------------------------------------------------------

async def signup(req: SignUpRequest):
    # Check username via DB
    if profile_service.username_exists(req.username):
        raise HTTPException(status_code=409, detail="Este username ja esta em uso.")

    data = _supabase_signup(req.email, req.password, req.name, req.username)

    # Supabase may return session immediately or require email confirmation
    session = data.get("session")
    user = data.get("user", {})

    if session:
        return AuthTokens(
            access_token=session["access_token"],
            refresh_token=session["refresh_token"],
            user={"id": user.get("id"), "email": user.get("email"), "name": req.name, "username": req.username},
        )

    return {"message": "Conta criada. Verifique seu email para confirmar.", "user_id": user.get("id")}


async def signin(req: SignInRequest):
    email = req.identifier

    # Resolve username to email if needed
    if "@" not in req.identifier:
        resolved = profile_service.get_email_by_username(req.identifier)
        if not resolved:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado.")
        email = resolved

    data = _supabase_signin(email, req.password)

    user = data.get("user", {})
    metadata = user.get("user_metadata", {})

    return AuthTokens(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        user={
            "id": user.get("id"),
            "email": user.get("email"),
            "name": metadata.get("name"),
            "username": metadata.get("username"),
        },
    )


async def refresh(req: RefreshRequest):
    data = _supabase_refresh(req.refresh_token)

    user = data.get("user", {})
    metadata = user.get("user_metadata", {})

    return AuthTokens(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        user={
            "id": user.get("id"),
            "email": user.get("email"),
            "name": metadata.get("name"),
            "username": metadata.get("username"),
        },
    )


async def me(user_id: str = Depends(get_current_user)):
    return {"id": user_id}
