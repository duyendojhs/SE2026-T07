"""Unit tests for BaseRule, RuleFinding, StalePRRule and StaleIssueRule."""

from __future__ import annotations

import dataclasses
from datetime import UTC, datetime, timedelta

import pytest

from app.services.rules import (
    BaseRule,
    IssueMeta,
    ItemState,
    PullRequestMeta,
    RepositorySnapshot,
    RuleFinding,
    Severity,
    StaleIssueRule,
    StalePRRule,
)

NOW = datetime(2026, 11, 12, tzinfo=UTC)


def _pr(number: int, age: timedelta, state: ItemState = ItemState.OPEN) -> PullRequestMeta:
    return PullRequestMeta(number=number, state=state, last_activity_at=NOW - age)


def _snap(*prs: PullRequestMeta) -> RepositorySnapshot:
    return RepositorySnapshot(pull_requests=tuple(prs))


# --- RuleFinding / BaseRule -------------------------------------------------


def test_rule_finding_schema_fields() -> None:
    names = {f.name for f in dataclasses.fields(RuleFinding)}
    assert {"rule_id", "severity", "title", "trigger_reason", "impacted_items", "metrics"} <= names


def test_rule_finding_has_no_individual_level_fields() -> None:
    names = {f.name for f in dataclasses.fields(RuleFinding)}
    assert not names & {"author", "user", "member", "score", "grade"}


def test_rule_finding_rejects_empty_reason() -> None:
    with pytest.raises(ValueError):
        RuleFinding("r", Severity.LOW, "t", "  ", ())


def test_rule_finding_rejects_empty_rule_id() -> None:
    with pytest.raises(ValueError):
        RuleFinding("", Severity.LOW, "t", "reason", ())


def test_base_rule_is_abstract() -> None:
    with pytest.raises(TypeError):
        BaseRule()  # type: ignore[abstract]


def test_subclass_without_rule_id_is_rejected() -> None:
    class NoId(BaseRule):
        def _evaluate(self, snapshot: RepositorySnapshot, now: datetime) -> list[RuleFinding]:
            return []

    with pytest.raises(TypeError):
        NoId()


def test_evaluate_rejects_naive_now() -> None:
    with pytest.raises(ValueError):
        StalePRRule().evaluate(_snap(), datetime(2026, 11, 12))  # noqa: DTZ001


def test_naive_activity_timestamp_rejected() -> None:
    with pytest.raises(ValueError):
        PullRequestMeta(1, ItemState.OPEN, datetime(2026, 11, 1))  # noqa: DTZ001


# --- StalePRRule ------------------------------------------------------------


def test_default_pr_threshold_is_three_days() -> None:
    assert StalePRRule().threshold == timedelta(days=3)


def test_no_prs_no_findings() -> None:
    assert StalePRRule().evaluate(_snap(), NOW) == []


def test_exactly_three_days_is_not_stale() -> None:
    assert StalePRRule().evaluate(_snap(_pr(1, timedelta(days=3))), NOW) == []


def test_just_over_three_days_is_stale() -> None:
    findings = StalePRRule().evaluate(_snap(_pr(1, timedelta(days=3, seconds=1))), NOW)
    assert len(findings) == 1
    assert findings[0].impacted_items == ("PR #1",)


def test_future_activity_is_not_stale() -> None:
    assert StalePRRule().evaluate(_snap(_pr(1, timedelta(days=-1))), NOW) == []


@pytest.mark.parametrize("state", [ItemState.CLOSED, ItemState.MERGED])
def test_non_open_prs_ignored(state: ItemState) -> None:
    assert StalePRRule().evaluate(_snap(_pr(1, timedelta(days=30), state)), NOW) == []


def test_impacted_items_sorted_by_number() -> None:
    snap = _snap(_pr(9, timedelta(days=5)), _pr(2, timedelta(days=4)))
    (finding,) = StalePRRule().evaluate(snap, NOW)
    assert finding.impacted_items == ("PR #2", "PR #9")


def test_finding_is_explainable() -> None:
    snap = _snap(_pr(1, timedelta(days=4)), _pr(2, timedelta(hours=1)))
    (finding,) = StalePRRule().evaluate(snap, NOW)
    assert finding.rule_id == "stale_pr"
    assert "1 of 2 open PR(s)" in finding.trigger_reason
    assert "72 hours" in finding.trigger_reason
    assert finding.metrics == {
        "open_count": 2,
        "stale_count": 1,
        "threshold_hours": 72.0,
        "max_inactive_hours": 96.0,
    }


def test_severity_medium_below_twice_threshold() -> None:
    (finding,) = StalePRRule().evaluate(_snap(_pr(1, timedelta(days=5, hours=23))), NOW)
    assert finding.severity is Severity.MEDIUM


def test_severity_high_at_twice_threshold() -> None:
    (finding,) = StalePRRule().evaluate(_snap(_pr(1, timedelta(days=6))), NOW)
    assert finding.severity is Severity.HIGH


def test_custom_threshold() -> None:
    rule = StalePRRule(threshold=timedelta(hours=12))
    (finding,) = rule.evaluate(_snap(_pr(1, timedelta(hours=13))), NOW)
    assert finding.metrics["threshold_hours"] == 12.0


@pytest.mark.parametrize("bad", [timedelta(0), timedelta(days=-1)])
def test_non_positive_threshold_rejected(bad: timedelta) -> None:
    with pytest.raises(ValueError):
        StalePRRule(threshold=bad)


def test_evaluation_is_deterministic() -> None:
    snap = _snap(_pr(1, timedelta(days=4)), _pr(2, timedelta(days=9)))
    rule = StalePRRule()
    assert rule.evaluate(snap, NOW) == rule.evaluate(snap, NOW)


# --- StaleIssueRule ---------------------------------------------------------


def test_stale_issue_default_threshold_and_detection() -> None:
    rule = StaleIssueRule()
    assert rule.threshold == timedelta(days=7)
    snap = RepositorySnapshot(
        issues=(
            IssueMeta(1, ItemState.OPEN, NOW - timedelta(days=8)),
            IssueMeta(2, ItemState.OPEN, NOW - timedelta(days=7)),
            IssueMeta(3, ItemState.CLOSED, NOW - timedelta(days=40)),
        )
    )
    (finding,) = rule.evaluate(snap, NOW)
    assert finding.rule_id == "stale_issue"
    assert finding.impacted_items == ("Issue #1",)
    assert finding.metrics["open_count"] == 2


# --- Mock fixture scenario (offline, tests/mocks/rules_snapshot.json) -------


def test_pr_rule_on_mock_snapshot(snapshot: RepositorySnapshot, now: datetime) -> None:
    (finding,) = StalePRRule().evaluate(snapshot, now)
    assert finding.impacted_items == ("PR #3", "PR #4", "PR #7")
    assert finding.severity is Severity.HIGH
    assert finding.metrics["open_count"] == 5
    assert finding.metrics["max_inactive_hours"] == 264.0


def test_issue_rule_on_mock_snapshot(snapshot: RepositorySnapshot, now: datetime) -> None:
    (finding,) = StaleIssueRule().evaluate(snapshot, now)
    assert finding.impacted_items == ("Issue #10",)
    assert finding.severity is Severity.MEDIUM
    assert finding.metrics["max_inactive_hours"] == 192.0
