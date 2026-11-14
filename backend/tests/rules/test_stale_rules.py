from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.services.rules.stale import StaleIssueRule, StalePRRule


def test_stale_pr_rule_flags_inactive_open_pull_request() -> None:
    stale_pr = {
        "number": 42,
        "state": "open",
        "updated_at": (datetime.now(UTC) - timedelta(days=4)).isoformat(),
    }

    findings = StalePRRule().evaluate([stale_pr])

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "stale-pr"
    assert finding.severity == "warning"
    assert "Pull request #42" in finding.trigger_reason
    assert finding.impacted_items == ["pr#42"]


def test_stale_issue_rule_flags_inactive_open_issue() -> None:
    stale_issue = {
        "number": 7,
        "state": "open",
        "updated_at": (datetime.now(UTC) - timedelta(days=5)).isoformat(),
    }

    findings = StaleIssueRule().evaluate([stale_issue])

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "stale-issue"
    assert finding.severity == "warning"
    assert "Issue #7" in finding.trigger_reason
    assert finding.impacted_items == ["issue#7"]


def test_stale_rules_ignore_active_or_closed_items() -> None:
    active_pr = {
        "number": 99,
        "state": "open",
        "updated_at": (datetime.now(UTC) - timedelta(days=1)).isoformat(),
    }
    closed_issue = {
        "number": 100,
        "state": "closed",
        "updated_at": (datetime.now(UTC) - timedelta(days=90)).isoformat(),
    }

    assert StalePRRule().evaluate([active_pr]) == []
    assert StaleIssueRule().evaluate([closed_issue]) == []
