"""GitHub App authentication: app JWT and installation tokens."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import jwt

from app.core.config import settings


class GitHubAppNotConfigured(RuntimeError):
    """Raised when App credentials are missing."""


class GitHubAPIError(RuntimeError):
    """A GitHub API call failed."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code


class GitHubAppAuth:
    """Small GitHub App auth adapter.

    App JWTs authenticate the App; installation tokens are short-lived and are
    never persisted. A user PAT is never accepted as a fallback.
    """

    def __init__(
        self,
        *,
        app_id: int | None = None,
        private_key: str | None = None,
        private_key_path: str | None = None,
        base_url: str | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.app_id = app_id if app_id is not None else settings.github_app_id
        self.private_key = private_key or settings.github_private_key
        self.private_key_path = private_key_path or settings.github_private_key_path
        self.base_url = (base_url or settings.github_api_url).rstrip("/")
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=30,
            transport=transport,
            headers={"Accept": "application/vnd.github+json"},
        )

    @property
    def configured(self) -> bool:
        return bool(self.app_id and self._key_material())

    def _key_material(self) -> str | None:
        if self.private_key:
            return self.private_key
        if self.private_key_path:
            path = Path(self.private_key_path)
            if path.exists():
                return path.read_text(encoding="utf-8")
        return None

    def app_jwt(self) -> str:
        if not self.app_id:
            raise GitHubAppNotConfigured("GITHUB_APP_ID is not configured")
        key = self._key_material()
        if not key:
            raise GitHubAppNotConfigured("GitHub App private key is not configured")
        now = datetime.now(UTC)
        payload = {
            "iat": int((now - timedelta(seconds=60)).timestamp()),
            "exp": int((now + timedelta(minutes=9)).timestamp()),
            "iss": str(self.app_id),
        }
        return jwt.encode(payload, key, algorithm="RS256")

    def _app_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.app_jwt()}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def installation_token(self, installation_id: int) -> str:
        response = self.client.post(
            f"/app/installations/{installation_id}/access_tokens",
            headers=self._app_headers(),
        )
        if response.status_code >= 400:
            raise GitHubAPIError(
                response.status_code,
                f"installation token failed with status {response.status_code}",
            )
        payload: dict[str, Any] = response.json()
        token = payload.get("token")
        if not token:
            raise GitHubAPIError(500, "installation token missing from response")
        return str(token)

    def installation(self, installation_id: int) -> dict[str, Any]:
        response = self.client.get(
            f"/app/installations/{installation_id}",
            headers=self._app_headers(),
        )
        if response.status_code >= 400:
            raise GitHubAPIError(
                response.status_code,
                f"installation lookup failed with status {response.status_code}",
            )
        payload: dict[str, Any] = response.json()
        return payload

    def installation_repositories(self, installation_id: int) -> list[dict[str, Any]]:
        token = self.installation_token(installation_id)
        response = self.client.get(
            "/installation/repositories",
            params={"per_page": 100},
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        if response.status_code >= 400:
            raise GitHubAPIError(
                response.status_code,
                f"installation repositories failed with status {response.status_code}",
            )
        payload: dict[str, Any] = response.json()
        repositories = payload.get("repositories") or []
        return [item for item in repositories if isinstance(item, dict)]

    def close(self) -> None:
        self.client.close()

