from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, Mapping, Sequence

from app.services.rules.base import BaseRule, RuleFinding


def _as_list(items: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None) -> list[Mapping[str, Any]]:
    if items is None:
        return []
    if isinstance(items, Mapping):
        return [items]
    return list(items)


def _parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(raw)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
    return None


class StalePRRule(BaseRule):
    """Flag open pull requests older than 3 days."""

    rule_id = "stale-pr"
    severity = "warning"
    title = "Open pull request is stale"

    def evaluate(
        self,
        items: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None,
    ) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        now = datetime.now(UTC)
        threshold = timedelta(days=3)

        for item in _as_list(items):
            if str(item.get("state", "")).lower() != "open":
                continue

            updated_at = _parse_datetime(item.get("updated_at"))
            if updated_at is None:
                continue

            age = now - updated_at
            if age <= threshold:
                continue

            number = item.get("number") or item.get("id") or "unknown"
            trigger_reason = (
                f"Pull request #{number} is open and has had no activity for "
                f"{age.total_seconds() / 86400:.1f} days."
            )
            findings.append(
                RuleFinding(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    title=self.title,
                    trigger_reason=trigger_reason,
                    impacted_items=[f"pr#{number}"],
                )
            )

        return findings


class StaleIssueRule(BaseRule):
    """Flag open issues older than 3 days."""

    rule_id = "stale-issue"
    severity = "warning"
    title = "Open issue is stale"

    def evaluate(
        self,
        items: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None,
    ) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        now = datetime.now(UTC)
        threshold = timedelta(days=3)

        for item in _as_list(items):
            if str(item.get("state", "")).lower() != "open":
                continue

            updated_at = _parse_datetime(item.get("updated_at"))
            if updated_at is None:
                continue

            age = now - updated_at
            if age <= threshold:
                continue

            number = item.get("number") or item.get("id") or "unknown"
            trigger_reason = (
                f"Issue #{number} is open and has had no activity for "
                f"{age.total_seconds() / 86400:.1f} days."
            )
            findings.append(
                RuleFinding(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    title=self.title,
                    trigger_reason=trigger_reason,
                    impacted_items=[f"issue#{number}"],
                )
            )

        return findings


__all__ = ["StalePRRule", "StaleIssueRule"]
