from sqlalchemy import text
from sqlmodel import Session, select

from app.audit.service import AuditService
from app.models import AuditCheckpoint, Tenant


def test_audit_chain_verifies_and_stores_only_actor_hash(session: Session) -> None:
    tenant = Tenant(slug="audit-test", name="Audit Test")
    session.add(tenant)
    session.commit()

    service = AuditService(secret="test-secret")
    entry = service.append(
        session,
        tenant_id=tenant.id,
        actor_id="alice@example.com",
        action="github.backfill",
        resource="duyendojhs/SE2026-T07/issues",
        request_payload={"repo": "duyendojhs/SE2026-T07"},
    )
    session.commit()

    assert entry.actor_hash != "alice@example.com"
    assert "alice" not in entry.actor_hash
    assert "example.com" not in entry.actor_hash
    assert session.exec(select(AuditCheckpoint)).first() is not None
    assert service.verify(session, tenant_id=tenant.id)["valid"] is True


def test_audit_tampering_is_detected(session: Session) -> None:
    tenant = Tenant(slug="tamper-test", name="Tamper Test")
    session.add(tenant)
    session.commit()
    service = AuditService(secret="test-secret")
    entry = service.append(
        session,
        tenant_id=tenant.id,
        actor_id="system:test",
        action="github.fetch",
        resource="repo",
    )
    session.commit()

    session.connection().execute(
        text("UPDATE audit_logs SET action = :action WHERE id = :id"),
        {"action": "tampered", "id": entry.id.hex},
    )
    session.commit()

    result = service.verify(session, tenant_id=tenant.id)

    assert result["valid"] is False
    assert result["reason"] == "entry hash mismatch"


def test_missing_audit_entry_breaks_the_chain(session: Session) -> None:
    tenant = Tenant(slug="delete-test", name="Delete Test")
    session.add(tenant)
    session.commit()
    service = AuditService(secret="test-secret")
    first = service.append(
        session,
        tenant_id=tenant.id,
        actor_id="system:test",
        action="first",
        resource="repo",
    )
    service.append(
        session,
        tenant_id=tenant.id,
        actor_id="system:test",
        action="second",
        resource="repo",
    )
    session.commit()

    session.connection().execute(
        text("DELETE FROM audit_logs WHERE id = :id"),
        {"id": first.id.hex},
    )
    session.commit()

    result = service.verify(session, tenant_id=tenant.id)

    assert result["valid"] is False
    assert result["reason"] in {"prev_hash mismatch", "checkpoint entry is missing"}

