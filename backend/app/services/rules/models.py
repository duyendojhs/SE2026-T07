"""Metadata-only input models consumed by the rule engine.

Zero-Code Retention: these models deliberately carry no comment bodies, commit
bodies, diffs, patches, file contents, or author identities. Rules therefore
cannot produce individual-level findings even by accident.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class ItemState(StrEnum):
    """Lifecycle state of a pull request or issue."""

    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


def require_aware(value: datetime, name: str) -> None:
    """Raise ``ValueError`` if ``value`` is a naive (timezone-less) datetime."""
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValueError(f"{name} must be timezone-aware")


@dataclass(frozen=True, slots=True)
class PullRequestMeta:
    """Metadata of a pull request.

    ``last_activity_at`` is the latest timestamp among pushes, review events,
    comment events (timestamp only, never the body) and state changes.
    """

    number: int
    state: ItemState
    last_activity_at: datetime
    is_draft: bool = False

    def __post_init__(self) -> None:
        require_aware(self.last_activity_at, "last_activity_at")


@dataclass(frozen=True, slots=True)
class IssueMeta:
    """Metadata of an issue (``last_activity_at`` as for pull requests)."""

    number: int
    state: ItemState
    last_activity_at: datetime

    def __post_init__(self) -> None:
        require_aware(self.last_activity_at, "last_activity_at")


@dataclass(frozen=True, slots=True)
class RepositorySnapshot:
    """Team-level, metadata-only view of one repository at a point in time."""

    pull_requests: tuple[PullRequestMeta, ...] = ()
    issues: tuple[IssueMeta, ...] = ()
