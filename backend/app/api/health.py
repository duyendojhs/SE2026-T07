"""Liveness and readiness endpoints."""

from __future__ import annotations

from typing import Annotated

import redis
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlmodel import Session

from app.core.config import settings
from app.db import get_session

router = APIRouter(tags=["system"])


def ping_redis() -> None:
    client = redis.Redis.from_url(settings.redis_url, socket_connect_timeout=2)
    try:
        client.ping()
    finally:
        client.close()


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "github-project-coach",
        "environment": settings.app_env,
    }


@router.get("/ready")
def ready(session: Annotated[Session, Depends(get_session)]) -> dict[str, str]:
    try:
        session.connection().execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - environment failure
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        ) from exc
    try:
        ping_redis()
    except Exception as exc:  # pragma: no cover - environment failure
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="redis unavailable",
        ) from exc
    return {"status": "ok", "database": "ok", "redis": "ok"}
