"""Append-only, per-tenant audit hash chain."""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from datetime import UTC, datetime
from typing import Any, cast

from sqlalchemy import event
from sqlmodel import Session, select

from app.core.config import settings
from app.models import AuditCheckpoint, AuditLog, utcnow

GENESIS = "0" * 64
CHECKPOINT_EVERY = 1_000


class AuditIntegrityError(RuntimeError):
    """Raised when an audit entry cannot be appended safely."""


def _utc_iso(timestamp: datetime) -> str:
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC).isoformat()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def entry_digest(
    *,
    prev_hash: str,
    timestamp: datetime,
    tenant_id: uuid.UUID,
    actor_hash: str,
    action: str,
    resource: str,
    request_hash: str,
) -> str:
    material = "|".join(
        [
            prev_hash,
            _utc_iso(timestamp),
            str(tenant_id),
            actor_hash,
            action,
            resource,
            request_hash,
        ]
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


class AuditService:
    """Append and verify tenant-scoped audit chains."""

    def __init__(self, secret: str | None = None) -> None:
        self.secret = (secret or settings.audit_hmac_secret).encode("utf-8")

    def actor_hash(self, actor_id: str) -> str:
        return hmac.new(self.secret, actor_id.encode("utf-8"), hashlib.sha256).hexdigest()

    def request_hash(self, payload: Any | None) -> str:
        if payload is None:
            return hashlib.sha256(b"").hexdigest()
        return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()

    def append(
        self,
        session: Session,
        *,
        tenant_id: uuid.UUID,
        actor_id: str,
        action: str,
        resource: str,
        request_payload: Any | None = None,
    ) -> AuditLog:
        last = session.exec(
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(cast(Any, AuditLog.created_at).desc(), cast(Any, AuditLog.id).desc())
        ).first()
        prev_hash = last.entry_hash if last else GENESIS
        timestamp = utcnow()
        actor_hash = self.actor_hash(actor_id)
        request_hash = self.request_hash(request_payload)
        digest = entry_digest(
            prev_hash=prev_hash,
            timestamp=timestamp,
            tenant_id=tenant_id,
            actor_hash=actor_hash,
            action=action,
            resource=resource,
            request_hash=request_hash,
        )
        entry = AuditLog(
            tenant_id=tenant_id,
            actor_hash=actor_hash,
            action=action,
            resource=resource,
            request_hash=request_hash,
            prev_hash=prev_hash,
            entry_hash=digest,
            created_at=timestamp,
        )
        session.add(entry)
        try:
            session.flush()
        except Exception as exc:  # pragma: no cover - defensive for concurrent writers
            session.rollback()
            raise AuditIntegrityError("audit chain append conflicted") from exc

        count = len(
            session.exec(select(AuditLog.id).where(AuditLog.tenant_id == tenant_id)).all()
        )
        if count == 1 or count % CHECKPOINT_EVERY == 0:
            self.create_checkpoint(session, tenant_id=tenant_id)
        return entry

    def create_checkpoint(
        self, session: Session, *, tenant_id: uuid.UUID
    ) -> AuditCheckpoint:
        latest = session.exec(
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(cast(Any, AuditLog.created_at).desc(), cast(Any, AuditLog.id).desc())
        ).first()
        if latest is None:
            raise AuditIntegrityError("cannot checkpoint an empty audit chain")
        existing = session.exec(
            select(AuditCheckpoint).where(
                AuditCheckpoint.tenant_id == tenant_id,
                AuditCheckpoint.upto_entry_id == latest.id,
            )
        ).first()
        if existing:
            return existing
        checkpoint = AuditCheckpoint(
            tenant_id=tenant_id,
            upto_entry_id=latest.id,
            hash=latest.entry_hash,
        )
        session.add(checkpoint)
        session.flush()
        return checkpoint

    def verify(self, session: Session, *, tenant_id: uuid.UUID) -> dict[str, Any]:
        entries = session.exec(
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(cast(Any, AuditLog.created_at), cast(Any, AuditLog.id))
        ).all()
        checkpoints = session.exec(
            select(AuditCheckpoint)
            .where(AuditCheckpoint.tenant_id == tenant_id)
            .order_by(cast(Any, AuditCheckpoint.created_at).desc())
        ).all()

        if not entries:
            return {
                "valid": True,
                "checked_entries": 0,
                "checkpoint_id": None,
                "reason": "empty chain",
            }

        if not checkpoints:
            return {
                "valid": "unknown",
                "checked_entries": 0,
                "checkpoint_id": None,
                "reason": "no checkpoint available",
            }

        latest_checkpoint = checkpoints[0]
        checkpoint_entry = session.get(AuditLog, latest_checkpoint.upto_entry_id)
        if checkpoint_entry is None:
            return {
                "valid": False,
                "checked_entries": 0,
                "checkpoint_id": str(latest_checkpoint.id),
                "reason": "checkpoint entry is missing",
            }
        if checkpoint_entry.entry_hash != latest_checkpoint.hash:
            return {
                "valid": False,
                "checked_entries": 0,
                "checkpoint_id": str(latest_checkpoint.id),
                "reason": "checkpoint hash mismatch",
            }

        prev_hash = GENESIS
        for entry in entries:
            if entry.prev_hash != prev_hash:
                return {
                    "valid": False,
                    "checked_entries": 0,
                    "checkpoint_id": str(latest_checkpoint.id),
                    "reason": "prev_hash mismatch",
                }
            expected = entry_digest(
                prev_hash=entry.prev_hash,
                timestamp=entry.created_at,
                tenant_id=entry.tenant_id,
                actor_hash=entry.actor_hash,
                action=entry.action,
                resource=entry.resource,
                request_hash=entry.request_hash,
            )
            if entry.entry_hash != expected:
                return {
                    "valid": False,
                    "checked_entries": 0,
                    "checkpoint_id": str(latest_checkpoint.id),
                    "reason": "entry hash mismatch",
                }
            prev_hash = entry.entry_hash

        return {
            "valid": True,
            "checked_entries": len(entries),
            "checkpoint_id": str(latest_checkpoint.id),
            "reason": "chain and checkpoint verified",
        }


@event.listens_for(AuditLog, "before_update")
def _block_audit_update(*_: Any) -> None:
    raise AuditIntegrityError("audit entries are append-only")


@event.listens_for(AuditLog, "before_delete")
def _block_audit_delete(*_: Any) -> None:
    raise AuditIntegrityError("audit entries are append-only")



