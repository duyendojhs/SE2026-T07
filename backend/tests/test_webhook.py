import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.models import Installation, RawEvent, Repository, Tenant


def _signature(body: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def test_webhook_deduplicates_and_strips_content(
    client: TestClient, session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    tenant = Tenant(slug="webhook-test", name="Webhook Test")
    session.add(tenant)
    session.commit()
    installation = Installation(
        tenant_id=tenant.id,
        installation_id=777,
        account_login="duyendojhs",
    )
    session.add(installation)
    session.commit()
    repo = Repository(
        tenant_id=tenant.id,
        installation_id=installation.id,
        github_id=888,
        full_name="duyendojhs/SE2026-T07",
    )
    session.add(repo)
    session.commit()

    payload = {
        "action": "opened",
        "installation": {"id": 777},
        "repository": {"id": 888, "full_name": "duyendojhs/SE2026-T07"},
        "issue": {
            "number": 1,
            "title": "metadata",
            "body": "must not be stored",
            "patch": "must not be stored",
            "authorization": "Bearer secret",
            "token": "secret",
        },
    }
    body = json.dumps(payload).encode()
    secret = "test-webhook-secret"
    monkeypatch.setattr(settings, "github_webhook_secret", secret)
    headers = {
        "X-GitHub-Event": "issues",
        "X-GitHub-Delivery": "delivery-1",
        "X-Hub-Signature-256": _signature(body, secret),
        "Content-Type": "application/json",
    }

    first = client.post("/api/v1/webhooks/github", content=body, headers=headers)
    second = client.post("/api/v1/webhooks/github", content=body, headers=headers)

    assert first.status_code == 202
    assert first.json() == {"status": "accepted"}
    assert second.status_code == 202
    assert second.json() == {"status": "duplicate"}
    events = session.exec(select(RawEvent)).all()
    assert len(events) == 1
    assert "body" not in events[0].payload_json["issue"]
    assert "patch" not in events[0].payload_json["issue"]
    assert "authorization" not in events[0].payload_json["issue"]
    assert "token" not in events[0].payload_json["issue"]


def test_webhook_rejects_bad_signature(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "github_webhook_secret", "test-secret")
    response = client.post(
        "/api/v1/webhooks/github",
        content=b"{}",
        headers={
            "X-GitHub-Event": "issues",
            "X-GitHub-Delivery": "delivery-bad",
            "X-Hub-Signature-256": "sha256=bad",
        },
    )

    assert response.status_code == 401


