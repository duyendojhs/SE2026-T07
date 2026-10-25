"""Signed HttpOnly session cookies and short-lived OAuth state."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import Request, Response
from pydantic import BaseModel

from app.core.config import settings


class SessionData(BaseModel):
    github_id: int
    login: str
    tenant_slug: str | None = None
    role: str = "member"


class SessionError(ValueError):
    """Invalid or expired session."""


def create_session_token(data: SessionData, *, ttl_seconds: int | None = None) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        **data.model_dump(),
        "purpose": "session",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl_seconds or settings.session_ttl_seconds)).timestamp()),
    }
    return jwt.encode(payload, settings.session_secret, algorithm="HS256")


def decode_session_token(token: str) -> SessionData:
    try:
        payload = jwt.decode(token, settings.session_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise SessionError("invalid session token") from exc
    if payload.get("purpose") != "session":
        raise SessionError("wrong token purpose")
    try:
        return SessionData(
            github_id=int(payload["github_id"]),
            login=str(payload["login"]),
            tenant_slug=payload.get("tenant_slug"),
            role=str(payload.get("role") or "member"),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise SessionError("incomplete session token") from exc


def session_from_request(request: Request) -> SessionData | None:
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        return None
    try:
        return decode_session_token(token)
    except SessionError:
        return None


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=settings.session_ttl_seconds,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(settings.session_cookie_name, path="/")


def set_oauth_state_cookie(response: Response, state: str) -> None:
    response.set_cookie(
        key=settings.oauth_state_cookie_name,
        value=state,
        max_age=600,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def clear_oauth_state_cookie(response: Response) -> None:
    response.delete_cookie(settings.oauth_state_cookie_name, path="/")


def create_oauth_state() -> str:
    now = datetime.now(UTC)
    payload = {
        "purpose": "oauth_state",
        "nonce": secrets.token_urlsafe(24),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=10)).timestamp()),
    }
    return jwt.encode(payload, settings.session_secret, algorithm="HS256")


def validate_oauth_state(state: str) -> None:
    try:
        payload = jwt.decode(state, settings.session_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise SessionError("invalid OAuth state") from exc
    if payload.get("purpose") != "oauth_state":
        raise SessionError("wrong OAuth state purpose")
