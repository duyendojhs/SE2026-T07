"""Endpoint and field allowlists for the metadata-only GitHub client."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlsplit

_ALLOWED_PATTERNS = (
    re.compile(r"^/repos/[^/]+/[^/]+$"),
    re.compile(r"^/repos/[^/]+/[^/]+/issues$"),
    re.compile(r"^/repos/[^/]+/[^/]+/issues/\d+/comments$"),
    re.compile(r"^/repos/[^/]+/[^/]+/pulls$"),
    re.compile(r"^/repos/[^/]+/[^/]+/pulls/\d+/reviews$"),
    re.compile(r"^/repos/[^/]+/[^/]+/commits$"),
    re.compile(r"^/repos/[^/]+/[^/]+/collaborators$"),
    re.compile(r"^/installation/repositories$"),
    re.compile(r"^/app/installations/\d+$"),
    re.compile(r"^/user$"),
)

_BANNED_PATTERNS = (
    re.compile(r"/contents(?:/|$)"),
    re.compile(r"/git/blobs(?:/|$)"),
    re.compile(r"/compare(?:/|$)"),
    re.compile(r"/pulls/\d+/files$"),
    re.compile(r"/actions(?:/|$)"),
)

BANNED_KEYS = {
    "patch",
    "diff",
    "blob",
    "content",
    "raw_content",
    "file_content",
    "encoded_content",
    "body",
    "comment_body",
    "commit_body",
    "message",
    "authorization",
    "token",
    "access_token",
    "refresh_token",
    "private_key",
    "client_secret",
    "password",
    "secret",
}


class EndpointNotAllowed(ValueError):
    """Raised when a caller tries to access a non-allowlisted GitHub endpoint."""


def endpoint_path(path_or_url: str) -> str:
    """Return a path without query/fragment for allowlist checks."""

    parts = urlsplit(path_or_url)
    return parts.path or path_or_url.split("?", 1)[0]


def assert_allowed(path_or_url: str) -> None:
    """Reject content, diff, blob, and other non-metadata endpoints."""

    path = endpoint_path(path_or_url)
    if any(pattern.search(path) for pattern in _BANNED_PATTERNS):
        raise EndpointNotAllowed(f"endpoint is not metadata-only: {path}")
    if not any(pattern.match(path) for pattern in _ALLOWED_PATTERNS):
        raise EndpointNotAllowed(f"endpoint is not allowlisted: {path}")


def is_allowed(path_or_url: str) -> bool:
    try:
        assert_allowed(path_or_url)
    except EndpointNotAllowed:
        return False
    return True


def strip_payload(value: Any) -> tuple[Any, int]:
    """Recursively remove banned keys and return (clean_value, stripped_count)."""

    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        stripped = 0
        for key, child in value.items():
            if str(key).lower() in BANNED_KEYS:
                stripped += 1
                continue
            cleaned_child, child_stripped = strip_payload(child)
            clean[key] = cleaned_child
            stripped += child_stripped
        return clean, stripped
    if isinstance(value, list):
        clean_list: list[Any] = []
        stripped = 0
        for child in value:
            cleaned_child, child_stripped = strip_payload(child)
            clean_list.append(cleaned_child)
            stripped += child_stripped
        return clean_list, stripped
    return value, 0


def commit_subject(payload: dict[str, Any]) -> str:
    """Read commit.message transiently and keep only its first line."""

    commit = payload.get("commit") or {}
    message = commit.get("message") or ""
    return str(message).splitlines()[0][:200] if str(message) else ""


def comment_metadata(payload: dict[str, Any]) -> tuple[int, bool]:
    """Derive comment metadata without persisting the body."""

    body = str(payload.get("body") or "")
    return len(body), "```" in body
