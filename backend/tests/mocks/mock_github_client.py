"""Offline GitHub API client backed by synthetic metadata fixtures."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from copy import deepcopy
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


class MockGitHubClient:
    """Return local fixture pages for supported GitHub REST endpoints.

    The interface intentionally matches the ``paginate`` method used by
    ``BackfillService``. No HTTP client or network transport is constructed.
    """

    _REPOSITORY_ENDPOINT = re.compile(r"^/repos/[^/]+/[^/]+/(?P<resource>pulls|issues|commits)$")
    _REVIEWS_ENDPOINT = re.compile(
        r"^/repos/[^/]+/[^/]+/pulls/(?P<number>\d+)/reviews$"
    )

    def __init__(self, fixtures_dir: Path | None = None) -> None:
        directory = fixtures_dir or Path(__file__).parent
        self._pull_requests = self._load_list(directory / "prs_mock.json", "pull_requests")
        self._reviews = self._load_reviews(directory / "prs_mock.json")
        self._issues = self._load_list(directory / "issues_mock.json", "issues")
        self._commits = self._load_list(directory / "commits_mock.json", "commits")

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise TypeError(f"Fixture root must be a JSON object: {path.name}")
        return payload

    @classmethod
    def _load_list(cls, path: Path, key: str) -> list[dict[str, Any]]:
        payload = cls._read_json(path)
        items = payload.get(key)
        if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
            raise ValueError(f"Fixture '{path.name}' must contain a list of objects at '{key}'")
        return items

    @classmethod
    def _load_reviews(cls, path: Path) -> dict[str, list[dict[str, Any]]]:
        reviews = cls._read_json(path).get("reviews")
        if not isinstance(reviews, dict):
            raise TypeError(f"Fixture '{path.name}' must contain a reviews object")
        if any(
            not isinstance(items, list) or any(not isinstance(item, dict) for item in items)
            for items in reviews.values()
        ):
            raise ValueError(f"Fixture '{path.name}' reviews must be lists of objects")
        return reviews

    def paginate(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Iterator[list[dict[str, Any]]]:
        """Yield one independent fixture page for a supported endpoint."""

        del params  # The synthetic fixtures are intentionally small and unpaginated.
        endpoint = urlsplit(path).path.rstrip("/")
        reviews_match = self._REVIEWS_ENDPOINT.fullmatch(endpoint)
        if reviews_match:
            records = self._reviews.get(reviews_match.group("number"), [])
        else:
            endpoint_match = self._REPOSITORY_ENDPOINT.fullmatch(endpoint)
            if endpoint_match is None:
                raise ValueError(f"Unsupported mock GitHub endpoint: {endpoint}")
            resource = endpoint_match.group("resource")
            records = {
                "pulls": self._pull_requests,
                "issues": self._issues,
                "commits": self._commits,
            }[resource]

        yield deepcopy(records)

    def close(self) -> None:
        """Match the real client's lifecycle method; there are no resources to close."""
