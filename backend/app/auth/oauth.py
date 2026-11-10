"""GitHub OAuth identity flow. The user token is transient and never stored."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import httpx

from app.core.config import settings


class GitHubOAuthNotConfigured(RuntimeError):
    """Raised when OAuth client credentials are missing."""


class GitHubOAuthError(RuntimeError):
    """Raised when GitHub rejects an OAuth exchange or user lookup."""


class GitHubOAuth:
    def __init__(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        oauth_url: str | None = None,
        api_url: str | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.client_id = client_id or settings.github_client_id
        self.client_secret = client_secret or settings.github_client_secret
        self.oauth_url = (oauth_url or settings.github_oauth_url).rstrip("/")
        self.api_url = (api_url or settings.github_api_url).rstrip("/")
        self.transport = transport

    @property
    def configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def authorize_url(self, *, state: str) -> str:
        if not self.client_id:
            raise GitHubOAuthNotConfigured("GITHUB_CLIENT_ID is not configured")
        query = urlencode(
            {
                "client_id": self.client_id,
                "redirect_uri": settings.github_oauth_redirect_uri,
                "state": state,
                "scope": "read:user",
            }
        )
        return f"https://github.com/login/oauth/authorize?{query}"

    def exchange_code(self, code: str) -> str:
        if not self.configured:
            raise GitHubOAuthNotConfigured("GitHub OAuth is not configured")
        with httpx.Client(timeout=30, transport=self.transport) as client:
            response = client.post(
                f"{self.oauth_url}/access_token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": settings.github_oauth_redirect_uri,
                },
                headers={"Accept": "application/json"},
            )
        if response.status_code >= 400:
            raise GitHubOAuthError(f"OAuth exchange failed with {response.status_code}")
        payload: dict[str, Any] = response.json()
        token = payload.get("access_token")
        if not token:
            raise GitHubOAuthError("OAuth response did not contain an access token")
        return str(token)

    def get_user(self, token: str) -> dict[str, Any]:
        with httpx.Client(timeout=30, transport=self.transport) as client:
            response = client.get(
                f"{self.api_url}/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
        if response.status_code >= 400:
            raise GitHubOAuthError(f"GitHub user lookup failed with {response.status_code}")
        payload: dict[str, Any] = response.json()
        if "id" not in payload or "login" not in payload:
            raise GitHubOAuthError("GitHub user payload is incomplete")
        return payload
