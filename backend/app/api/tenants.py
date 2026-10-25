"""Tenant-scoped repository, sync, and audit endpoints."""

from __future__ import annotations

import uuid
from typing import Any, cast

from fastapi import APIRouter, HTTPException, Request
from sqlmodel import select

from app.api.deps import DbSession
from app.audit.service import AuditService
from app.auth.dependencies import require_role, require_session, require_tenant
from app.core.config import settings
from app.github.app_auth import GitHubAPIError, GitHubAppAuth, GitHubAppNotConfigured
from app.github.client import GitHubClient
from app.ingestion.backfill import BackfillService
from app.models import AuditLog, Installation, Repository

router = APIRouter(prefix="/api/v1/tenants/{slug}", tags=["tenants"])


def build_github_client(installation_id: int) -> GitHubClient:
    app_auth = GitHubAppAuth()
    if not app_auth.configured:
        app_auth.close()
        raise GitHubAppNotConfigured("GitHub App is not configured")
    token = app_auth.installation_token(installation_id)
    app_auth.close()
    return GitHubClient(token_provider=lambda: token)


@router.get("/repos")
def list_repos(session: DbSession, request: Request, slug: str) -> list[dict[str, Any]]:
    current = require_tenant(slug, require_session(request))
    require_role(current, "owner", "member", "viewer")
    repos = session.exec(
        select(Repository).where(Repository.tenant_id == _tenant_id(session, slug))
    ).all()
    return [
        {
            "id": str(repo.id),
            "github_id": repo.github_id,
            "full_name": repo.full_name,
            "default_branch": repo.default_branch,
            "private": repo.private,
            "sync_status": repo.sync_status,
            "last_synced_at": repo.last_synced_at,
        }
        for repo in repos
    ]


@router.post("/repos/{repo_id}/sync")
def sync_repo(
    session: DbSession,
    request: Request,
    slug: str,
    repo_id: uuid.UUID,
) -> dict[str, Any]:
    current = require_tenant(slug, require_session(request))
    require_role(current, "owner", "member")
    repo = session.exec(
        select(Repository).where(
            Repository.id == repo_id,
            Repository.tenant_id == _tenant_id(session, slug),
        )
    ).first()
    if repo is None:
        raise HTTPException(status_code=404, detail="repository not found")
    if repo.installation_id is None:
        raise HTTPException(status_code=400, detail="repository has no installation")
    installation = session.get(Installation, repo.installation_id)
    if installation is None:
        raise HTTPException(status_code=400, detail="installation not found")
    try:
        client = build_github_client(installation.installation_id)
    except GitHubAppNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GitHubAPIError as exc:
        raise HTTPException(status_code=502, detail="GitHub client authentication failed") from exc
    try:
        result = BackfillService(
            session,
            client,
            tenant_id=repo.tenant_id,
            repo=repo,
            audit=AuditService(),
        ).run()
    finally:
        client.close()
    return {
        "status": result.status,
        "counts": result.counts,
        "errors": result.errors,
        "backfill_days": settings.backfill_days,
    }


@router.get("/audit")
def audit_log(
    session: DbSession, request: Request, slug: str, limit: int = 100
) -> list[dict[str, Any]]:
    current = require_tenant(slug, require_session(request))
    require_role(current, "owner", "member", "viewer")
    tenant_id = _tenant_id(session, slug)
    entries = session.exec(
        select(AuditLog)
        .where(AuditLog.tenant_id == tenant_id)
        .order_by(cast(Any, AuditLog.created_at).desc())
        .limit(min(max(limit, 1), 500))
    ).all()
    return [
        {
            "id": str(entry.id),
            "actor_hash": entry.actor_hash,
            "action": entry.action,
            "resource": entry.resource,
            "request_hash": entry.request_hash,
            "prev_hash": entry.prev_hash,
            "entry_hash": entry.entry_hash,
            "created_at": entry.created_at,
        }
        for entry in entries
    ]


@router.get("/audit/verify")
def verify_audit(session: DbSession, request: Request, slug: str) -> dict[str, Any]:
    current = require_tenant(slug, require_session(request))
    require_role(current, "owner", "member", "viewer")
    return AuditService().verify(session, tenant_id=_tenant_id(session, slug))


def _tenant_id(session: DbSession, slug: str) -> uuid.UUID:
    from app.models import Tenant

    tenant = session.exec(select(Tenant).where(Tenant.slug == slug)).first()
    if tenant is None:
        raise HTTPException(status_code=404, detail="tenant not found")
    return tenant.id


