"""GitHub OAuth, App installation callback, and current-user endpoint."""

from __future__ import annotations

import secrets

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlmodel import select

from app.api.deps import DbSession
from app.auth.dependencies import require_session
from app.auth.oauth import GitHubOAuth, GitHubOAuthError, GitHubOAuthNotConfigured
from app.auth.service import (
    ensure_tenant,
    provision_user,
    upsert_installation,
    upsert_repository,
)
from app.auth.session import (
    SessionData,
    SessionError,
    clear_oauth_state_cookie,
    clear_session_cookie,
    create_oauth_state,
    create_session_token,
    set_oauth_state_cookie,
    set_session_cookie,
    validate_oauth_state,
)
from app.core.config import settings
from app.github.app_auth import GitHubAPIError, GitHubAppAuth, GitHubAppNotConfigured
from app.models import Member, Tenant

router = APIRouter(prefix="/api/v1", tags=["auth"])


@router.get("/auth/github/login")
def github_login() -> RedirectResponse:
    oauth = GitHubOAuth()
    if not oauth.configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth is not configured",
        )
    state = create_oauth_state()
    response = RedirectResponse(oauth.authorize_url(state=state))
    set_oauth_state_cookie(response, state)
    return response


@router.get("/auth/github/callback")
def github_callback(
    session: DbSession,
    request: Request,
    code: str = Query(...),
    state: str = Query(...),
) -> RedirectResponse:
    try:
        validate_oauth_state(state)
    except SessionError as exc:
        raise HTTPException(status_code=400, detail="invalid OAuth state") from exc
    cookie_state = request.cookies.get(settings.oauth_state_cookie_name)
    if not cookie_state or not secrets.compare_digest(cookie_state, state):
        raise HTTPException(status_code=400, detail="OAuth state cookie mismatch")
    oauth = GitHubOAuth()
    try:
        token = oauth.exchange_code(code)
        user = oauth.get_user(token)
    except GitHubOAuthNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GitHubOAuthError as exc:
        raise HTTPException(status_code=502, detail="GitHub OAuth failed") from exc

    tenant, member = provision_user(session, user=user)
    data = SessionData(
        github_id=member.github_id,
        login=member.login,
        tenant_slug=tenant.slug,
        role=member.role,
    )
    response = RedirectResponse(f"{settings.frontend_url}/?connected=1")
    clear_oauth_state_cookie(response)
    set_session_cookie(response, create_session_token(data))
    return response


@router.get("/auth/github/install")
def github_install() -> RedirectResponse:
    if not settings.github_app_slug:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub App slug is not configured",
        )
    return RedirectResponse(
        f"https://github.com/apps/{settings.github_app_slug}/installations/new"
    )


@router.get("/auth/github/install/callback")
def github_install_callback(
    session: DbSession,
    request: Request,
    installation_id: int = Query(...),
) -> RedirectResponse:
    current = require_session(request)
    try:
        app_auth = GitHubAppAuth()
        if not app_auth.configured:
            raise GitHubAppNotConfigured
        installation_payload = app_auth.installation(installation_id)
        repositories = app_auth.installation_repositories(installation_id)
    except GitHubAppNotConfigured as exc:
        raise HTTPException(status_code=503, detail="GitHub App is not configured") from exc
    except GitHubAPIError as exc:
        raise HTTPException(status_code=502, detail="GitHub App installation failed") from exc
    finally:
        if "app_auth" in locals():
            app_auth.close()

    account = installation_payload.get("account") or {}
    account_login = str(account.get("login") or current.login)
    tenant = ensure_tenant(session)
    installation = upsert_installation(
        session,
        tenant_id=tenant.id,
        installation_id=installation_id,
        account_login=account_login,
        suspended=bool(installation_payload.get("suspended_at")),
    )
    for repository_payload in repositories:
        upsert_repository(
            session,
            tenant_id=tenant.id,
            installation_id=installation.id,
            payload=repository_payload,
        )
    member = session.exec(
        select(Member).where(
            Member.tenant_id == tenant.id,
            Member.github_id == current.github_id,
        )
    ).first()
    session.commit()
    role = member.role if member else current.role
    response = RedirectResponse(f"{settings.frontend_url}/?installed=1")
    set_session_cookie(
        response,
        create_session_token(
            SessionData(
                github_id=current.github_id,
                login=current.login,
                tenant_slug=tenant.slug,
                role=role,
            )
        ),
    )
    return response


@router.post("/auth/logout")
def logout() -> RedirectResponse:
    response = RedirectResponse(settings.frontend_url)
    clear_session_cookie(response)
    return response


@router.get("/me")
def me(session: DbSession, request: Request) -> dict[str, object]:
    current = require_session(request)
    tenant = session.exec(select(Tenant).where(Tenant.slug == current.tenant_slug)).first()
    member: Member | None = None
    if tenant is not None:
        member = session.exec(
            select(Member).where(
                Member.tenant_id == tenant.id,
                Member.github_id == current.github_id,
            )
        ).first()
    return {
        "github_id": current.github_id,
        "login": current.login,
        "tenant_slug": current.tenant_slug,
        "role": member.role if member else current.role,
        "member_id": str(member.id) if member else None,
    }
