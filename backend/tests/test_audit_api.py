from fastapi.testclient import TestClient
from sqlmodel import Session

from app.audit.service import AuditService
from app.auth.session import SessionData, create_session_token
from app.models import Tenant


def test_audit_api_returns_hash_not_login(
    client: TestClient, session: Session
) -> None:
    tenant = Tenant(slug="audit-api", name="Audit API")
    session.add(tenant)
    session.commit()
    AuditService(secret="test-secret").append(
        session,
        tenant_id=tenant.id,
        actor_id="alice@example.com",
        action="github.fetch",
        resource="repo",
    )
    session.commit()

    token = create_session_token(
        SessionData(github_id=1, login="alice", tenant_slug="audit-api", role="owner")
    )
    client.cookies.set("gpc_session", token)

    response = client.get("/api/v1/tenants/audit-api/audit")
    verify = client.get("/api/v1/tenants/audit-api/audit/verify")

    assert response.status_code == 200
    entry = response.json()[0]
    assert set(entry) >= {"actor_hash", "entry_hash", "prev_hash", "created_at"}
    assert "alice" not in str(entry)
    assert "example.com" not in str(entry)
    assert verify.status_code == 200
    assert verify.json()["valid"] is True
