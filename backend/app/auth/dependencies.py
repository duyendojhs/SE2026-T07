"""FastAPI dependencies for authenticated, tenant-scoped requests."""

from __future__ import annotations

from fastapi import HTTPException, Request, status

from app.auth.session import SessionData, session_from_request


def get_session(request: Request) -> SessionData | None:
    return session_from_request(request)


def require_session(request: Request) -> SessionData:
    session = session_from_request(request)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication required",
        )
    return session


def require_tenant(slug: str, session: SessionData) -> SessionData:
    if session.tenant_slug != slug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="tenant access denied",
        )
    return session


def require_role(session: SessionData, *roles: str) -> SessionData:
    if session.role not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="insufficient role",
        )
    return session
