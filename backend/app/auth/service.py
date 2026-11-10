"""Tenant/member/installation provisioning for the single team workspace."""

from __future__ import annotations

import uuid
from typing import Any

from sqlmodel import Session, func, select

from app.core.config import settings
from app.models import Installation, Member, Repository, Tenant


def ensure_tenant(session: Session, *, slug: str | None = None, name: str | None = None) -> Tenant:
    tenant_slug = slug or settings.tenant_slug
    tenant = session.exec(select(Tenant).where(Tenant.slug == tenant_slug)).first()
    if tenant is None:
        tenant = Tenant(slug=tenant_slug, name=name or settings.tenant_name)
        session.add(tenant)
        session.flush()
    return tenant


def ensure_member(
    session: Session,
    *,
    tenant_id: uuid.UUID,
    github_id: int,
    login: str,
    display_name: str | None = None,
) -> Member:
    member = session.exec(
        select(Member).where(Member.tenant_id == tenant_id, Member.github_id == github_id)
    ).first()
    member_count = session.exec(
        select(func.count()).select_from(Member).where(Member.tenant_id == tenant_id)
    ).one()
    if member is None:
        member = Member(
            tenant_id=tenant_id,
            github_id=github_id,
            login=login,
            display_name=display_name,
            role="owner" if member_count == 0 else "member",
        )
        session.add(member)
        session.flush()
    else:
        member.login = login
        member.display_name = display_name or member.display_name
        session.add(member)
    return member


def provision_user(session: Session, *, user: dict[str, Any]) -> tuple[Tenant, Member]:
    tenant = ensure_tenant(session)
    member = ensure_member(
        session,
        tenant_id=tenant.id,
        github_id=int(user["id"]),
        login=str(user["login"]),
        display_name=user.get("name"),
    )
    session.commit()
    return tenant, member


def upsert_installation(
    session: Session,
    *,
    tenant_id: uuid.UUID,
    installation_id: int,
    account_login: str,
    suspended: bool = False,
) -> Installation:
    installation = session.exec(
        select(Installation).where(Installation.installation_id == installation_id)
    ).first()
    if installation is None:
        installation = Installation(
            tenant_id=tenant_id,
            installation_id=installation_id,
            account_login=account_login,
            suspended=suspended,
        )
        session.add(installation)
        session.flush()
    else:
        installation.tenant_id = tenant_id
        installation.account_login = account_login
        installation.suspended = suspended
        session.add(installation)
    return installation


def upsert_repository(
    session: Session,
    *,
    tenant_id: uuid.UUID,
    installation_id: uuid.UUID,
    payload: dict[str, Any],
) -> Repository:
    github_id = int(payload["id"])
    repo = session.exec(
        select(Repository).where(
            Repository.tenant_id == tenant_id,
            Repository.github_id == github_id,
        )
    ).first()
    full_name = str(payload["full_name"])
    if repo is None:
        repo = Repository(
            tenant_id=tenant_id,
            installation_id=installation_id,
            github_id=github_id,
            full_name=full_name,
            default_branch=str(payload.get("default_branch") or "main"),
            private=bool(payload.get("private")),
        )
        session.add(repo)
    else:
        repo.installation_id = installation_id
        repo.full_name = full_name
        repo.default_branch = str(payload.get("default_branch") or "main")
        repo.private = bool(payload.get("private"))
        session.add(repo)
    session.flush()
    return repo
