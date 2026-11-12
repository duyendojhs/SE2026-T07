"""Stale pull request and stale issue detection rules."""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import ClassVar

from app.services.rules.base import BaseRule, RuleFinding, Severity
from app.services.rules.models import (
    IssueMeta,
    ItemState,
    PullRequestMeta,
    RepositorySnapshot,
)

SECONDS_PER_HOUR = 3600
ESCALATION_FACTOR = 2


def _format_duration(delta: timedelta) -> str:
    total_hours = int(delta.total_seconds() // SECONDS_PER_HOUR)
    days, hours = divmod(total_hours, 24)
    return f"{days} day(s) {hours} hour(s)"


class _StaleItemRule(BaseRule):
    """Shared logic: flag open items inactive for strictly longer than a threshold.

    Severity is rule-based and deterministic: ``HIGH`` when the longest
    inactivity is at least twice the threshold, otherwise ``MEDIUM``.
    """

    item_label: ClassVar[str]
    default_threshold: ClassVar[timedelta]

    def __init__(self, threshold: timedelta | None = None) -> None:
        super().__init__()
        self.threshold = threshold if threshold is not None else self.default_threshold
        if self.threshold <= timedelta(0):
            raise ValueError("threshold must be positive")

    @abstractmethod
    def _open_items(self, snapshot: RepositorySnapshot) -> Sequence[tuple[int, datetime]]:
        """Return ``(number, last_activity_at)`` for every open item."""

    def _evaluate(self, snapshot: RepositorySnapshot, now: datetime) -> list[RuleFinding]:
        open_items = self._open_items(snapshot)
        stale = sorted(
            (
                (number, now - last_activity)
                for number, last_activity in open_items
                if now - last_activity > self.threshold
            ),
            key=lambda pair: pair[0],
        )
        if not stale:
            return []

        longest = max(inactive for _, inactive in stale)
        threshold_hours = self.threshold.total_seconds() / SECONDS_PER_HOUR
        severity = (
            Severity.HIGH if longest >= self.threshold * ESCALATION_FACTOR else Severity.MEDIUM
        )
        reason = (
            f"{len(stale)} of {len(open_items)} open {self.item_label}(s) have had no "
            f"recorded activity for more than {_format_duration(self.threshold)} "
            f"(threshold: {threshold_hours:g} hours); the longest inactivity is "
            f"{_format_duration(longest)}."
        )
        return [
            RuleFinding(
                rule_id=self.rule_id,
                severity=severity,
                title=self.title,
                trigger_reason=reason,
                impacted_items=tuple(f"{self.item_label} #{number}" for number, _ in stale),
                metrics={
                    "open_count": len(open_items),
                    "stale_count": len(stale),
                    "threshold_hours": round(threshold_hours, 2),
                    "max_inactive_hours": round(longest.total_seconds() / SECONDS_PER_HOUR, 2),
                },
            )
        ]


class StalePRRule(_StaleItemRule):
    """Flag open pull requests with no activity for more than 3 days."""

    rule_id: ClassVar[str] = "stale_pr"
    title: ClassVar[str] = "Stale pull requests"
    item_label: ClassVar[str] = "PR"
    default_threshold: ClassVar[timedelta] = timedelta(days=3)

    def _open_items(self, snapshot: RepositorySnapshot) -> Sequence[tuple[int, datetime]]:
        prs: tuple[PullRequestMeta, ...] = snapshot.pull_requests
        return [(pr.number, pr.last_activity_at) for pr in prs if pr.state is ItemState.OPEN]


class StaleIssueRule(_StaleItemRule):
    """Flag open issues with no activity for more than 7 days (configurable)."""

    rule_id: ClassVar[str] = "stale_issue"
    title: ClassVar[str] = "Stale issues"
    item_label: ClassVar[str] = "Issue"
    default_threshold: ClassVar[timedelta] = timedelta(days=7)

    def _open_items(self, snapshot: RepositorySnapshot) -> Sequence[tuple[int, datetime]]:
        issues: tuple[IssueMeta, ...] = snapshot.issues
        return [(i.number, i.last_activity_at) for i in issues if i.state is ItemState.OPEN]
