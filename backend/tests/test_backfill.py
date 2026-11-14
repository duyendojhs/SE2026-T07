from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from sqlmodel import Session, select

from app.ingestion.backfill import BackfillService
from app.models import (
    Comment,
    Commit,
    Installation,
    Issue,
    PullRequest,
    RawEvent,
    Repository,
    Review,
    Tenant,
)

_MISSING_TITLE = object()


class FakeGitHubClient:
    def __init__(
        self,
        *,
        fail_reviews: bool = False,
        issue_title: Any = "Issue",
        issue_state: str = "open",
        issue_labels: list[dict[str, str]] | None = None,
    ) -> None:
        self.fail_reviews = fail_reviews
        self.issue_title = issue_title
        self.issue_state = issue_state
        self.issue_labels = issue_labels if issue_labels is not None else [{"name": "bug"}]
        self.now = datetime.now(UTC)

    def _timestamp(self, days_ago: int) -> str:
        return (self.now - timedelta(days=days_ago)).isoformat()

    def paginate(
        self, path: str, *, params: dict[str, Any] | None = None
    ) -> Iterator[list[dict[str, Any]]]:
        if path.endswith("/issues"):
            issue = {
                "id": 1001,
                "number": 7,
                "body": "private issue body",
                "state": self.issue_state,
                "user": {"login": "alice"},
                "assignees": [{"login": "bob"}],
                "labels": self.issue_labels,
                "created_at": self._timestamp(3),
                "updated_at": self._timestamp(1),
            }
            if self.issue_title is not _MISSING_TITLE:
                issue["title"] = self.issue_title
            yield [issue]
        elif path.endswith("/pulls"):
            yield [
                {
                    "id": 2001,
                    "number": 12,
                    "title": "PR",
                    "state": "closed",
                    "merged_at": self._timestamp(1),
                    "closed_at": self._timestamp(1),
                    "draft": False,
                    "user": {"login": "alice"},
                    "base": {"ref": "main"},
                    "head": {"sha": "a" * 40},
                    "merge_commit_sha": "b" * 40,
                    "created_at": self._timestamp(3),
                    "updated_at": self._timestamp(1),
                }
            ]
        elif "/pulls/12/reviews" in path:
            if self.fail_reviews:
                raise RuntimeError("review endpoint unavailable")
            yield [
                {
                    "id": 3001,
                    "user": {"login": "reviewer"},
                    "state": "APPROVED",
                    "submitted_at": self._timestamp(1),
                }
            ]
        elif "/issues/7/comments" in path:
            yield [
                {
                    "id": 4001,
                    "user": {"login": "commenter"},
                    "body": "issue comment",
                    "created_at": self._timestamp(1),
                    "updated_at": self._timestamp(1),
                }
            ]
        elif "/issues/12/comments" in path:
            yield [
                {
                    "id": 4002,
                    "user": {"login": "commenter"},
                    "body": "```\nreview note\n```",
                    "created_at": self._timestamp(1),
                    "updated_at": self._timestamp(1),
                }
            ]
        elif path.endswith("/commits"):
            yield [
                {
                    "sha": "c" * 40,
                    "author": {"login": "alice"},
                    "commit": {
                        "message": "feat: login\n\nbody",
                        "author": {"name": "Alice", "date": self._timestamp(1)},
                    },
                }
            ]
        else:
            yield []


def _seed(session: Session) -> tuple[Tenant, Repository]:
    tenant = Tenant(slug="backfill-test", name="Backfill Test")
    session.add(tenant)
    session.commit()
    installation = Installation(
        tenant_id=tenant.id,
        installation_id=9001,
        account_login="duyendojhs",
    )
    session.add(installation)
    session.commit()
    repo = Repository(
        tenant_id=tenant.id,
        installation_id=installation.id,
        github_id=555,
        full_name="duyendojhs/SE2026-T07",
    )
    session.add(repo)
    session.commit()
    return tenant, repo


def _seed_existing_issue(session: Session, tenant: Tenant, repo: Repository) -> Issue:
    issue = Issue(
        tenant_id=tenant.id,
        repo_id=repo.id,
        github_id=1001,
        number=7,
        title="Valid local title",
        state="open",
        labels=["old-label"],
        created_at=datetime(2026, 10, 1, tzinfo=UTC),
        updated_at=datetime(2026, 10, 2, tzinfo=UTC),
    )
    session.add(issue)
    session.commit()
    return issue


def test_backfill_is_idempotent_and_metadata_only(session: Session) -> None:
    tenant, repo = _seed(session)
    first = BackfillService(
        session,
        FakeGitHubClient(),
        tenant_id=tenant.id,
        repo=repo,
    ).run()

    assert first.status == "ready"
    assert first.counts == {
        "issues": 1,
        "pull_requests": 1,
        "reviews": 1,
        "comments": 2,
        "commits": 1,
    }
    assert len(session.exec(select(Issue)).all()) == 1
    assert len(session.exec(select(PullRequest)).all()) == 1
    assert len(session.exec(select(Review)).all()) == 1
    assert len(session.exec(select(Comment)).all()) == 2
    assert len(session.exec(select(Commit)).all()) == 1

    raw_events = session.exec(select(RawEvent)).all()
    assert raw_events
    for event in raw_events:
        assert "body" not in event.payload_json
        assert "patch" not in event.payload_json

    second = BackfillService(
        session,
        FakeGitHubClient(),
        tenant_id=tenant.id,
        repo=repo,
    ).run()

    assert second.status == "ready"
    assert len(session.exec(select(Issue)).all()) == 1
    assert len(session.exec(select(PullRequest)).all()) == 1
    assert len(session.exec(select(Review)).all()) == 1
    assert len(session.exec(select(Comment)).all()) == 2
    assert len(session.exec(select(Commit)).all()) == 1


def test_backfill_marks_partial_when_one_resource_fails(session: Session) -> None:
    tenant, repo = _seed(session)
    result = BackfillService(
        session,
        FakeGitHubClient(fail_reviews=True),
        tenant_id=tenant.id,
        repo=repo,
    ).run()

    assert result.status == "partial"
    assert any("review" in error for error in result.errors)
    assert len(session.exec(select(Issue)).all()) == 1


@pytest.mark.parametrize(
    "incoming_title",
    [_MISSING_TITLE, None, "", "   ", "x" * 501],
    ids=["missing", "null", "empty", "whitespace", "over-limit"],
)
def test_invalid_issue_title_preserves_old_title_but_updates_other_fields(
    session: Session, incoming_title: Any
) -> None:
    tenant, repo = _seed(session)
    _seed_existing_issue(session, tenant, repo)
    result = BackfillService(
        session,
        FakeGitHubClient(
            issue_title=incoming_title,
            issue_state="closed",
            issue_labels=[{"name": "new-label"}],
        ),
        tenant_id=tenant.id,
        repo=repo,
    ).run()

    saved = session.exec(select(Issue).where(Issue.repo_id == repo.id)).one()

    assert saved.title == "Valid local title"
    assert saved.state == "closed"
    assert saved.labels == ["new-label"]
    assert result.status == "partial"
    assert any("title" in error for error in result.errors)


def test_invalid_title_does_not_create_new_issue(session: Session) -> None:
    tenant, repo = _seed(session)
    result = BackfillService(
        session,
        FakeGitHubClient(issue_title=None),
        tenant_id=tenant.id,
        repo=repo,
    ).run()

    assert session.exec(select(Issue).where(Issue.repo_id == repo.id)).all() == []
    assert result.status == "partial"
    assert result.counts["issues"] == 0
    assert any("title" in error for error in result.errors)
