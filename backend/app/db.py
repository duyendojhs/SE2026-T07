"""Database engine and session helpers."""

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session for a request or task."""

    with Session(engine) as session:
        yield session


def init_db() -> None:
    """Create tables for local/test bootstrap.

    Production and CI use Alembic migrations; this helper exists for tests and
    throw-away local databases.
    """

    from app import models  # noqa: F401  # register SQLModel tables

    SQLModel.metadata.create_all(engine)
