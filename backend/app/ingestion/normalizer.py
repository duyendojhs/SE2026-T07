"""Turn allowlisted GitHub payloads into metadata-only row dictionaries."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from app.github.allowed_endpoints import comment_metadata, commit_subject


def parse_timestamp(value: Any, *, fallback: datetime | None = None) -> datetime:
    """Parse GitHub ISO timestamps and normalise to UTC."""

    if not value:
        return fallback or datetime.now(UTC)
    text = str(value).replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _login(value: Any) -> str | None:
    if isinstance(value, dict):
        login = value.get("login")
        return str(login) if login else None
    return None


def normalize_repository(
    payload: dict[str, Any], *, tenant_id: uuid.UUID, installation_id: uuid.UUID | None
) -> dict[str, Any]:
    return {
        "tenant_id": tenant_id,
        "installation_id": installation_id,
        "github_id": int(payload["id"]),
        "full_name": str(payload["full_name"]),
        "default_branch": str(payload.get("default_branch") or "main"),
        "private": bool(payload.get("private")),
    }


def normalize_issue(
    payload: dict[str, Any], *, tenant_id: uuid.UUID, repo_id: uuid.UUID
) -> dict[str, Any]:
    return {
        "tenant_id": tenant_id,
        "repo_id": repo_id,
        "github_id": int(payload["id"]),
        "number": int(payload["number"]),
        "title": str(payload.get("title") or "")[:500],
        "state": str(payload.get("state") or "open")[:20],
        "author_login": _login(payload.get("user")),
        "assignee_logins": [
            login
            for item in payload.get("assignees") or []
            if (login := _login(item)) is not None
        ],
        "labels": [
            str(item.get("name"))
            for item in payload.get("labels") or []
            if isinstance(item, dict) and item.get("name")
        ],
        "created_at": parse_timestamp(payload.get("created_at")),
        "updated_at": parse_timestamp(payload.get("updated_at")),
        "closed_at": (
            parse_timestamp(payload["closed_at"]) if payload.get("closed_at") else None
        ),
    }


def normalize_pull_request(
    payload: dict[str, Any], *, tenant_id: uuid.UUID, repo_id: uuid.UUID
) -> dict[str, Any]:
    merged_at = parse_timestamp(payload["merged_at"]) if payload.get("merged_at") else None
    state = "merged" if merged_at else str(payload.get("state") or "open")
    base = payload.get("base") or {}
    head = payload.get("head") or {}
    return {
        "tenant_id": tenant_id,
        "repo_id": repo_id,
        "github_id": int(payload["id"]),
        "number": int(payload["number"]),
        "title": str(payload.get("title") or "")[:500],
        "state": state[:20],
        "author_login": _login(payload.get("user")),
        "created_at": parse_timestamp(payload.get("created_at")),
        "updated_at": parse_timestamp(payload.get("updated_at")),
        "merged_at": merged_at,
        "closed_at": (
            parse_timestamp(payload["closed_at"]) if payload.get("closed_at") else None
        ),
        "is_draft": bool(payload.get("draft")),
        "additions": int(payload.get("additions") or 0),
        "deletions": int(payload.get("deletions") or 0),
        "changed_files": int(payload.get("changed_files") or 0),
        "base_branch": str(base.get("ref")) if base.get("ref") else None,
        "head_sha": str(head.get("sha")) if head.get("sha") else None,
        "merge_commit_sha": (
            str(payload["merge_commit_sha"]) if payload.get("merge_commit_sha") else None
        ),
    }


def normalize_review(
    payload: dict[str, Any],
    *,
    tenant_id: uuid.UUID,
    pr_id: uuid.UUID,
) -> dict[str, Any]:
    return {
        "tenant_id": tenant_id,
        "pr_id": pr_id,
        "github_id": int(payload["id"]),
        "reviewer_login": _login(payload.get("user")),
        "state": str(payload.get("state") or "UNKNOWN")[:50],
        "submitted_at": (
            parse_timestamp(payload["submitted_at"])
            if payload.get("submitted_at")
            else None
        ),
    }


def normalize_comment(
    payload: dict[str, Any],
    *,
    tenant_id: uuid.UUID,
    repo_id: uuid.UUID,
    parent_type: str,
    parent_id: int,
) -> dict[str, Any]:
    body_length, has_code_block = comment_metadata(payload)
    return {
        "tenant_id": tenant_id,
        "repo_id": repo_id,
        "github_id": int(payload["id"]),
        "parent_type": parent_type[:20],
        "parent_id": parent_id,
        "author_login": _login(payload.get("user")),
        "created_at": parse_timestamp(payload.get("created_at")),
        "updated_at": parse_timestamp(payload.get("updated_at")),
        "body_length": body_length,
        "has_code_block": has_code_block,
    }


def normalize_commit(
    payload: dict[str, Any],
    *,
    tenant_id: uuid.UUID,
    repo_id: uuid.UUID,
) -> dict[str, Any]:
    commit = payload.get("commit") or {}
    author = payload.get("author") or {}
    commit_author = commit.get("author") or {}
    return {
        "tenant_id": tenant_id,
        "repo_id": repo_id,
        "sha": str(payload["sha"])[:64],
        "author_login": _login(author) or (
            str(commit_author.get("name")) if commit_author.get("name") else None
        ),
        "committed_at": parse_timestamp(
            commit_author.get("date") or payload.get("created_at")
        ),
        "message_subject": commit_subject(payload),
    }
