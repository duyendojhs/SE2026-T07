"""Rate-limit-aware GitHub REST client with an endpoint allowlist."""

from __future__ import annotations

import random
import time
from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.config import settings
from app.github.allowed_endpoints import assert_allowed
from app.github.app_auth import GitHubAPIError


class GitHubClient:
    """Minimal metadata-only GitHub API reader.

    The client retries only transient failures. It never sends a PAT and never
    accepts a path outside ``allowed_endpoints``.
    """

    def __init__(
        self,
        *,
        token_provider: Callable[[], str],
        base_url: str | None = None,
        transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
        max_retries: int = 3,
        reserve: int | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.token_provider = token_provider
        self.base_url = (base_url or settings.github_api_url).rstrip("/")
        self.sleep = sleep
        self.max_retries = max_retries
        self.reserve = reserve if reserve is not None else settings.github_reserve_requests
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            transport=transport,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "SE2026-T07-GitHub-Project-Coach",
            },
        )
        self.remaining: int | None = None
        self.reset_at: datetime | None = None

    def _apply_rate_headers(self, response: httpx.Response) -> None:
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        if remaining is not None:
            try:
                self.remaining = int(remaining)
            except ValueError:
                self.remaining = None
        if reset is not None:
            try:
                self.reset_at = datetime.fromtimestamp(int(reset), tz=UTC)
            except ValueError:
                self.reset_at = None

    def _wait_for_reset(self) -> None:
        if self.remaining is None or self.remaining >= self.reserve:
            return
        if self.reset_at is None:
            return
        delay = max(0.0, (self.reset_at - datetime.now(UTC)).total_seconds())
        if delay:
            self.sleep(delay)

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        etag: str | None = None,
    ) -> httpx.Response:
        assert_allowed(path)
        headers: dict[str, str] = {}
        if etag:
            headers["If-None-Match"] = etag

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            self._wait_for_reset()
            headers["Authorization"] = f"Bearer {self.token_provider()}"
            response = self.client.request(
                method,
                path,
                params=params,
                headers=headers,
            )
            self._apply_rate_headers(response)

            if response.status_code == 304:
                return response
            if response.status_code in (401, 404):
                raise GitHubAPIError(
                    response.status_code,
                    f"GitHub request failed with status {response.status_code}",
                )
            if response.status_code in (403, 429):
                if attempt >= self.max_retries:
                    raise GitHubAPIError(
                        response.status_code,
                        "GitHub rate limit retries exhausted",
                    )
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    try:
                        self.sleep(float(retry_after))
                    except ValueError:
                        self.sleep(min(2**attempt, 60) + random.uniform(0, 1))
                else:
                    self.sleep(min(2**attempt, 60) + random.uniform(0, 1))
                last_error = GitHubAPIError(response.status_code, "rate limited")
                continue
            if response.status_code >= 500:
                if attempt >= self.max_retries:
                    raise GitHubAPIError(
                        response.status_code,
                        "GitHub server error retries exhausted",
                    )
                self.sleep(min(2**attempt, 60) + random.uniform(0, 1))
                last_error = GitHubAPIError(response.status_code, "server error")
                continue
            if response.status_code >= 400:
                raise GitHubAPIError(
                    response.status_code,
                    f"GitHub request failed with status {response.status_code}",
                )
            return response

        raise GitHubAPIError(500, f"GitHub request failed: {last_error}")

    def get_json(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        etag: str | None = None,
    ) -> tuple[Any, str | None]:
        response = self.request("GET", path, params=params, etag=etag)
        if response.status_code == 304:
            return None, etag
        return response.json(), response.headers.get("ETag")

    def paginate(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        etag: str | None = None,
    ) -> Iterator[list[dict[str, Any]]]:
        next_path: str | None = path
        next_params = params
        first = True
        while next_path is not None:
            response = self.request(
                "GET",
                next_path,
                params=next_params,
                etag=etag if first else None,
            )
            first = False
            if response.status_code == 304:
                return
            payload = response.json()
            if isinstance(payload, dict):
                items = payload.get("items") or payload.get("repositories") or []
            else:
                items = payload
            if not isinstance(items, list):
                return
            yield [item for item in items if isinstance(item, dict)]
            next_path = _next_link(response.headers.get("Link"))

    def close(self) -> None:
        self.client.close()


def _next_link(link_header: str | None) -> str | None:
    if not link_header:
        return None
    for part in link_header.split(","):
        section = part.strip()
        if 'rel="next"' not in section:
            continue
        url = section.split(";", 1)[0].strip()
        if url.startswith("<") and url.endswith(">"):
            return url[1:-1]
    return None
