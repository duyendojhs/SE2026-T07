"""GitHub webhook intake with signature verification and delivery dedupe."""

from __future__ import annotations

import hashlib
import json

from fastapi import APIRouter, Header, HTTPException, Request, status
from sqlmodel import select

from app.api.deps import DbSession
from app.audit.service import AuditService
from app.core.config import settings
from app.github.allowed_endpoints import strip_payload
from app.github.webhook import verify_signature
from app.models import Installation, ProcessedDelivery, RawEvent, Repository

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


@router.post("/github", status_code=status.HTTP_202_ACCEPTED)
async def github_webhook(
    session: DbSession,
    request: Request,
    x_github_event: str = Header(default="unknown"),
    x_github_delivery: str | None = Header(default=None),
    x_hub_signature_256: str | None = Header(default=None),
) -> dict[str, str]:
    if not settings.github_webhook_secret:
        raise HTTPException(status_code=503, detail="webhook secret is not configured")
    body = await request.body()
    if not verify_signature(body, x_hub_signature_256, settings.github_webhook_secret):
        raise HTTPException(status_code=401, detail="invalid webhook signature")
    if not x_github_delivery:
        raise HTTPException(status_code=400, detail="missing delivery id")
    if session.get(ProcessedDelivery, x_github_delivery) is not None:
        return {"status": "duplicate"}

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="invalid JSON payload") from exc
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="webhook payload must be an object")

    installation_payload = payload.get("installation") or {}
    installation_id = installation_payload.get("id")
    if not installation_id:
        raise HTTPException(status_code=400, detail="missing installation id")
    installation = session.exec(
        select(Installation).where(Installation.installation_id == int(installation_id))
    ).first()
    if installation is None:
        raise HTTPException(status_code=404, detail="installation not found")

    repository_payload = payload.get("repository") or {}
    repo: Repository | None = None
    if repository_payload.get("id"):
        repo = session.exec(
            select(Repository).where(
                Repository.tenant_id == installation.tenant_id,
                Repository.github_id == int(repository_payload["id"]),
            )
        ).first()

    clean, _ = strip_payload(payload)
    encoded = json.dumps(clean, sort_keys=True, separators=(",", ":"), default=str)
    event = RawEvent(
        tenant_id=installation.tenant_id,
        repo_id=repo.id if repo else None,
        delivery_id=x_github_delivery,
        event_type=x_github_event[:100],
        payload_json=clean,
        payload_hash=hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
    )
    session.add(event)
    session.add(ProcessedDelivery(delivery_id=x_github_delivery))
    AuditService().append(
        session,
        tenant_id=installation.tenant_id,
        actor_id="system:webhook",
        action="github.webhook",
        resource=x_github_event[:100],
        request_payload={"delivery_id": x_github_delivery, "event": x_github_event},
    )
    session.commit()
    return {"status": "accepted"}
