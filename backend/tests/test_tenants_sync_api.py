from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

from app import models  # noqa: F401
from app.auth.session import SessionData, create_session_token
from app.db import get_session
from app.main import app
from app.models import Installation, Repository, Tenant


class EmptyGitHubClient:
    def paginate(
        self, path: str, *, params: dict[str, Any] | None = None
    ) -> Generator[list[dict[str, Any]], None, None]:
        yield []

    def close(self) -> None:
        pass


def test_sync_api_does_not_return_success_when_persistence_fails(
    engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    with Session(engine) as seed_session:
        tenant = Tenant(slug="sync-api-failure", name="Sync API Failure")
        seed_session.add(tenant)
        seed_session.commit()
        installation = Installation(
            tenant_id=tenant.id,
            installation_id=99001,
            account_login="duyendojhs",
        )
        seed_session.add(installation)
        seed_session.commit()
        repo = Repository(
            tenant_id=tenant.id,
            installation_id=installation.id,
            github_id=99002,
            full_name="duyendojhs/SE2026-T07",
        )
        seed_session.add(repo)
        seed_session.commit()
        repo_id = repo.id

    def override_session() -> Generator[Session, None, None]:
        with Session(engine) as request_session:
            yield request_session

    def fail_commit(_: Session) -> None:
        raise SQLAlchemyError("injected API persistence failure")

    monkeypatch.setattr("app.api.tenants.build_github_client", lambda _: EmptyGitHubClient())
    event.listen(Session, "before_commit", fail_commit)
    app.dependency_overrides[get_session] = override_session
    try:
        token = create_session_token(
            SessionData(
                github_id=1,
                login="owner",
                tenant_slug="sync-api-failure",
                role="owner",
            )
        )
        with TestClient(app, raise_server_exceptions=False) as client:
            client.cookies.set("gpc_session", token)
            response = client.post(
                f"/api/v1/tenants/sync-api-failure/repos/{repo_id}/sync"
            )
        assert response.status_code == 500
        assert response.text == "Internal Server Error"
    finally:
        app.dependency_overrides.pop(get_session, None)
        event.remove(Session, "before_commit", fail_commit)

    with Session(engine) as verify_session:
        persisted_repo = verify_session.get(Repository, repo_id)
        assert persisted_repo is not None
        assert persisted_repo.sync_status == "pending"
