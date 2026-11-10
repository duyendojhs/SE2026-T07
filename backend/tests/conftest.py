from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app import models  # noqa: F401  # register tables
from app.db import get_session
from app.main import app


@pytest.fixture
def engine() -> Generator[Engine, None, None]:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def session(engine: Engine) -> Generator[Session, None, None]:
    with Session(engine) as db_session:
        yield db_session


@pytest.fixture
def client(engine: Engine) -> Generator[TestClient, None, None]:
    def override_session() -> Generator[Session, None, None]:
        with Session(engine) as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

