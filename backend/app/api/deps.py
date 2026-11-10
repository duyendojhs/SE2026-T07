"""Shared FastAPI dependencies."""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.db import get_session

DbSession = Annotated[Session, Depends(get_session)]


def session_dependency() -> Generator[Session, None, None]:
    yield from get_session()
