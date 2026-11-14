import uuid
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.api import tenants as tenant_api
from app.audit.service import AuditService
from app.auth.session import SessionData, create_session_token
from app.models import AuditLog, Installation, Issue, RawEvent, Repository, Tenant


class FakeGitHubClient:
    def __init__(self, *, title: Any) -> None:
        self.title = title

    def paginate(
        self, path: str, *, params: dict[str, Any] | None = None
    ) -> Iterator[list[dict[str, Any]]]:
        if path.endswith("/issues"):
            yield [
                {
                    "id": 1001,
                    "number": 7,
                    "title": self.title,
                    "state": "open",
                    "user": {"login": "alice"},
                    "assignees": [],
                    "labels": [],
                    "created_at": "2026-10-01T00:00:00Z",
                    "updated_at": "2026-10-02T00:00:00Z",
                }
            ]
        yield []

    def close(self) -> None:
        pass


def _seed_issue(
    session: Session, *, slug: str = "undo-test", title: str = "Old local title"
) -> tuple[Tenant, Repository, Issue]:
    tenant = Tenant(slug=slug, name="Undo Test")
    session.add(tenant)
    session.commit()
    installation = Installation(
        tenant_id=tenant.id,
        installation_id=9001,
        account_login="duyendojhs",
    )
    session.add(installation)
    session.commit()
    repo = Repository(
        tenant_id=tenant.id,
        installation_id=installation.id,
        github_id=555,
        full_name="duyendojhs/SE2026-T07",
    )
    session.add(repo)
    session.commit()
    issue = Issue(
        tenant_id=tenant.id,
        repo_id=repo.id,
        github_id=1001,
        number=7,
        title=title,
        state="open",
        labels=["old-label"],
        created_at=datetime(2026, 10, 1, tzinfo=UTC),
        updated_at=datetime(2026, 10, 2, tzinfo=UTC),
    )
    session.add(issue)
    session.commit()
    return tenant, repo, issue


def _login(client: TestClient, *, slug: str, role: str) -> None:
    token = create_session_token(
        SessionData(
            github_id=1,
            login=f"{role}-user",
            tenant_slug=slug,
            role=role,
        )
    )
    client.cookies.set("gpc_session", token)


def test_sync_response_identifies_issue_title_undo_handle(
    client: TestClient,
    session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, repo, issue = _seed_issue(session)
    source_title = "GITHUB-SOURCE-TITLE-SHOULD-NOT-BE-RETURNED"
    fake = FakeGitHubClient(title=source_title)
    monkeypatch.setattr(tenant_api, "build_github_client", lambda _: fake)
    _login(client, slug=tenant.slug, role="owner")

    response = client.post(f"/api/v1/tenants/{tenant.slug}/repos/{repo.id}/sync")

    assert response.status_code == 200
    handles = response.json()["issue_title_undo_handles"]
    assert len(handles) == 1
    handle = handles[0]
    assert set(handle) == {"issue_id", "issue_number", "sync_id"}
    assert handle["issue_id"] == str(issue.id)
    assert handle["issue_number"] == issue.number
    uuid.UUID(handle["sync_id"])
    assert source_title not in response.text

    session.expire_all()
    saved = session.get(Issue, issue.id)
    assert saved is not None
    assert saved.title == source_title
    assert saved.previous_title == "Old local title"
    raw_events = session.exec(select(RawEvent)).all()
    assert all("title" not in event.payload_json for event in raw_events)


def test_owner_can_undo_local_title_and_retry_safely(
    client: TestClient,
    session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, repo, issue = _seed_issue(session)
    fake = FakeGitHubClient(title="GITHUB-TITLE-AFTER-SYNC")
    monkeypatch.setattr(tenant_api, "build_github_client", lambda _: fake)
    _login(client, slug=tenant.slug, role="owner")
    sync_response = client.post(f"/api/v1/tenants/{tenant.slug}/repos/{repo.id}/sync")
    handle = sync_response.json()["issue_title_undo_handles"][0]
    undo_url = (
        f"/api/v1/tenants/{tenant.slug}/repos/{repo.id}/issues/{issue.id}/title/undo"
    )
    undo_params = {"sync_id": handle["sync_id"]}
    audit_count_before = len(session.exec(select(AuditLog)).all())

    undone = client.post(undo_url, params=undo_params)

    assert undone.status_code == 200
    assert undone.json()["status"] == "undone"
    session.expire_all()
    saved = session.get(Issue, issue.id)
    assert saved is not None
    assert saved.title == "Old local title"
    assert saved.previous_title is None
    assert saved.title_change_sync_id == uuid.UUID(handle["sync_id"])
    assert fake.title == "GITHUB-TITLE-AFTER-SYNC"
    audit_after_undo = session.exec(select(AuditLog)).all()
    assert len(audit_after_undo) == audit_count_before + 1
    undo_entries = [entry for entry in audit_after_undo if entry.action == "issue.title.undo"]
    assert len(undo_entries) == 1
    assert undo_entries[0].resource == f"repos/{repo.id}/issues/{issue.id}/title"
    assert "Old local title" not in str(audit_after_undo)
    assert "GITHUB-TITLE-AFTER-SYNC" not in str(audit_after_undo)
    assert AuditService().verify(session, tenant_id=tenant.id)["valid"] is True

    repeated = client.post(undo_url, params=undo_params)

    assert repeated.status_code == 200
    assert repeated.json()["status"] == "already_undone"
    assert len(session.exec(select(AuditLog)).all()) == audit_count_before + 1


def test_old_sync_handle_cannot_overwrite_a_later_title(
    client: TestClient,
    session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, repo, issue = _seed_issue(session)
    fake = FakeGitHubClient(title="First synced title")
    monkeypatch.setattr(tenant_api, "build_github_client", lambda _: fake)
    _login(client, slug=tenant.slug, role="owner")
    first = client.post(f"/api/v1/tenants/{tenant.slug}/repos/{repo.id}/sync")
    first_handle = first.json()["issue_title_undo_handles"][0]

    fake.title = "Later synced title"
    second = client.post(f"/api/v1/tenants/{tenant.slug}/repos/{repo.id}/sync")
    second_handle = second.json()["issue_title_undo_handles"][0]
    stale = client.post(
        f"/api/v1/tenants/{tenant.slug}/repos/{repo.id}/issues/{issue.id}/title/undo",
        params={"sync_id": first_handle["sync_id"]},
    )

    assert stale.status_code == 409
    session.expire_all()
    saved = session.get(Issue, issue.id)
    assert saved is not None
    assert saved.title == "Later synced title"
    assert saved.previous_title == "First synced title"
    assert saved.title_change_sync_id == uuid.UUID(second_handle["sync_id"])


def test_same_title_sync_keeps_current_undo_handle(
    client: TestClient,
    session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, repo, issue = _seed_issue(session)
    fake = FakeGitHubClient(title="First synced title")
    monkeypatch.setattr(tenant_api, "build_github_client", lambda _: fake)
    _login(client, slug=tenant.slug, role="owner")
    first = client.post(f"/api/v1/tenants/{tenant.slug}/repos/{repo.id}/sync")
    handle = first.json()["issue_title_undo_handles"][0]

    same_title_sync = client.post(f"/api/v1/tenants/{tenant.slug}/repos/{repo.id}/sync")

    assert same_title_sync.status_code == 200
    assert same_title_sync.json()["issue_title_undo_handles"] == []
    session.expire_all()
    saved = session.get(Issue, issue.id)
    assert saved is not None
    assert saved.title_change_sync_id == uuid.UUID(handle["sync_id"])
    assert saved.previous_title == "Old local title"


def test_invalid_title_sync_keeps_pending_handle(
    client: TestClient,
    session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, repo, issue = _seed_issue(session)
    fake = FakeGitHubClient(title="First synced title")
    monkeypatch.setattr(tenant_api, "build_github_client", lambda _: fake)
    _login(client, slug=tenant.slug, role="owner")
    first = client.post(f"/api/v1/tenants/{tenant.slug}/repos/{repo.id}/sync")
    handle = first.json()["issue_title_undo_handles"][0]

    fake.title = "x" * 501
    invalid_sync = client.post(f"/api/v1/tenants/{tenant.slug}/repos/{repo.id}/sync")

    assert invalid_sync.status_code == 200
    assert invalid_sync.json()["status"] == "partial"
    assert invalid_sync.json()["issue_title_undo_handles"] == []
    session.expire_all()
    saved = session.get(Issue, issue.id)
    assert saved is not None
    assert saved.title == "First synced title"
    assert saved.title_change_sync_id == uuid.UUID(handle["sync_id"])
    assert saved.previous_title == "Old local title"


def test_undo_rolls_back_when_audit_append_fails(
    client: TestClient,
    session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, repo, issue = _seed_issue(session)
    fake = FakeGitHubClient(title="Synced title")
    monkeypatch.setattr(tenant_api, "build_github_client", lambda _: fake)
    _login(client, slug=tenant.slug, role="owner")
    sync_response = client.post(f"/api/v1/tenants/{tenant.slug}/repos/{repo.id}/sync")
    handle = sync_response.json()["issue_title_undo_handles"][0]
    audit_count_before = len(session.exec(select(AuditLog)).all())

    def fail_append(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("audit append failed")

    monkeypatch.setattr(tenant_api.AuditService, "append", fail_append)
    undo_url = (
        f"/api/v1/tenants/{tenant.slug}/repos/{repo.id}/issues/{issue.id}/title/undo"
    )
    with pytest.raises(RuntimeError, match="audit append failed"):
        client.post(undo_url, params={"sync_id": handle["sync_id"]})

    session.expire_all()
    saved = session.get(Issue, issue.id)
    assert saved is not None
    assert saved.title == "Synced title"
    assert saved.previous_title == "Old local title"
    assert saved.title_change_sync_id == uuid.UUID(handle["sync_id"])
    assert len(session.exec(select(AuditLog)).all()) == audit_count_before


def test_authenticated_member_can_undo(
    client: TestClient,
    session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, repo, issue = _seed_issue(session)
    fake = FakeGitHubClient(title="Synced title")
    monkeypatch.setattr(tenant_api, "build_github_client", lambda _: fake)
    _login(client, slug=tenant.slug, role="member")
    sync_response = client.post(f"/api/v1/tenants/{tenant.slug}/repos/{repo.id}/sync")
    handle = sync_response.json()["issue_title_undo_handles"][0]

    undone = client.post(
        f"/api/v1/tenants/{tenant.slug}/repos/{repo.id}/issues/{issue.id}/title/undo",
        params={"sync_id": handle["sync_id"]},
    )

    assert undone.status_code == 200
    assert undone.json()["status"] == "undone"
    session.expire_all()
    saved = session.get(Issue, issue.id)
    assert saved is not None
    assert saved.title == "Old local title"


def test_authenticated_viewer_cannot_undo(
    client: TestClient,
    session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, repo, issue = _seed_issue(session)
    fake = FakeGitHubClient(title="Synced title")
    monkeypatch.setattr(tenant_api, "build_github_client", lambda _: fake)
    _login(client, slug=tenant.slug, role="owner")
    sync_response = client.post(f"/api/v1/tenants/{tenant.slug}/repos/{repo.id}/sync")
    handle = sync_response.json()["issue_title_undo_handles"][0]
    _login(client, slug=tenant.slug, role="viewer")

    denied = client.post(
        f"/api/v1/tenants/{tenant.slug}/repos/{repo.id}/issues/{issue.id}/title/undo",
        params={"sync_id": handle["sync_id"]},
    )

    assert denied.status_code == 403
    session.expire_all()
    saved = session.get(Issue, issue.id)
    assert saved is not None
    assert saved.title == "Synced title"


def test_unauthenticated_user_cannot_undo(
    client: TestClient,
    session: Session,
) -> None:
    tenant, repo, issue = _seed_issue(session)

    denied = client.post(
        f"/api/v1/tenants/{tenant.slug}/repos/{repo.id}/issues/{issue.id}/title/undo",
        params={"sync_id": str(uuid.uuid4())},
    )

    assert denied.status_code == 401


def test_owner_cannot_undo_issue_from_another_tenant(
    client: TestClient,
    session: Session,
) -> None:
    _tenant, repo, issue = _seed_issue(session, slug="alpha")
    beta = Tenant(slug="beta", name="Beta")
    session.add(beta)
    session.commit()
    _login(client, slug=beta.slug, role="owner")

    denied = client.post(
        f"/api/v1/tenants/{beta.slug}/repos/{repo.id}/issues/{issue.id}/title/undo",
        params={"sync_id": str(uuid.uuid4())},
    )

    assert denied.status_code == 404
    session.expire_all()
    saved = session.get(Issue, issue.id)
    assert saved is not None
    assert saved.title == "Old local title"
