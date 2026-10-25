from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.auth.session import (
    SessionData,
    SessionError,
    create_oauth_state,
    create_session_token,
    decode_session_token,
    validate_oauth_state,
)
from app.core.config import settings
from app.models import Repository, Tenant


def test_session_token_roundtrip() -> None:
    token = create_session_token(
        SessionData(github_id=1, login="alice", tenant_slug="alpha", role="owner")
    )

    decoded = decode_session_token(token)

    assert decoded.github_id == 1
    assert decoded.login == "alice"
    assert decoded.tenant_slug == "alpha"


def test_session_token_rejects_garbage() -> None:
    with pytest.raises(SessionError):
        decode_session_token("not-a-jwt")


def test_oauth_state_roundtrip() -> None:
    validate_oauth_state(create_oauth_state())


def test_tenant_isolation_for_repo_list(client: TestClient, session: Session) -> None:
    alpha = Tenant(slug="alpha", name="Alpha")
    beta = Tenant(slug="beta", name="Beta")
    session.add(alpha)
    session.add(beta)
    session.commit()
    session.add(
        Repository(
            tenant_id=alpha.id,
            github_id=1,
            full_name="duyendojhs/alpha",
        )
    )
    session.add(
        Repository(
            tenant_id=beta.id,
            github_id=2,
            full_name="duyendojhs/beta",
        )
    )
    session.commit()

    token = create_session_token(
        SessionData(github_id=1, login="alice", tenant_slug="alpha", role="owner")
    )
    client.cookies.set("gpc_session", token)

    allowed = client.get("/api/v1/tenants/alpha/repos")
    denied = client.get("/api/v1/tenants/beta/repos")

    assert allowed.status_code == 200
    assert [repo["full_name"] for repo in allowed.json()] == ["duyendojhs/alpha"]
    assert denied.status_code == 403


def test_me_requires_auth(client: TestClient) -> None:
    assert client.get("/api/v1/me").status_code == 401


def test_me_returns_session_identity(client: TestClient) -> None:
    token = create_session_token(
        SessionData(
            github_id=7,
            login="alice",
            tenant_slug="alpha",
            role="owner",
        )
    )
    client.cookies.set("gpc_session", token)

    response = client.get("/api/v1/me")

    assert response.status_code == 200
    assert response.json()["login"] == "alice"
    assert response.json()["tenant_slug"] == "alpha"


def test_session_token_expiry() -> None:
    token = create_session_token(
        SessionData(github_id=1, login="alice"),
        ttl_seconds=-1,
    )

    with pytest.raises(SessionError):
        decode_session_token(token)


def test_session_data_has_no_email_field() -> None:
    assert "email" not in SessionData.model_fields
    assert datetime.now(UTC).year >= 2026



def test_login_sets_oauth_state_cookie(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "github_client_id", "client-id")
    monkeypatch.setattr(settings, "github_client_secret", "client-secret")

    response = client.get("/api/v1/auth/github/login", follow_redirects=False)

    assert response.status_code in {302, 307}
    assert "github.com/login/oauth/authorize" in response.headers["location"]
    assert response.cookies.get(settings.oauth_state_cookie_name)

