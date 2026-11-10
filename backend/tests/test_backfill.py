from collections.abc import Iterator
from typing import Any

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


class FakeGitHubClient:
    def __init__(self, *, fail_reviews: bool = False) -> None:
        self.fail_reviews = fail_reviews

    def paginate(
        self, path: str, *, params: dict[str, Any] | None = None
    ) -> Iterator[list[dict[str, Any]]]:
        if path.endswith("/issues"):
            yield [
                {
                    "id": 1001,
                    "number": 7,
                    "title": "Issue",
                    "body": "private issue body",
                    "state": "open",
                    "user": {"login": "alice"},
                    "assignees": [{"login": "bob"}],
                    "labels": [{"name": "bug"}],
                    "created_at": "2026-10-01T00:00:00Z",
                    "updated_at": "2026-10-02T00:00:00Z",
                }
            ]
        elif path.endswith("/pulls"):
            yield [
                {
                    "id": 2001,
                    "number": 12,
                    "title": "PR",
                    "state": "closed",
                    "merged_at": "2026-10-03T00:00:00Z",
                    "closed_at": "2026-10-03T00:00:00Z",
                    "draft": False,
                    "user": {"login": "alice"},
                    "base": {"ref": "main"},
                    "head": {"sha": "a" * 40},
                    "merge_commit_sha": "b" * 40,
                    "created_at": "2026-10-01T00:00:00Z",
                    "updated_at": "2026-10-03T00:00:00Z",
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
                    "submitted_at": "2026-10-02T00:00:00Z",
                }
            ]
        elif "/issues/7/comments" in path:
            yield [
                {
                    "id": 4001,
                    "user": {"login": "commenter"},
                    "body": "issue comment",
                    "created_at": "2026-10-02T00:00:00Z",
                    "updated_at": "2026-10-02T00:00:00Z",
                }
            ]
        elif "/issues/12/comments" in path:
            yield [
                {
                    "id": 4002,
                    "user": {"login": "commenter"},
                    "body": "```\nreview note\n```",
                    "created_at": "2026-10-02T00:00:00Z",
                    "updated_at": "2026-10-02T00:00:00Z",
                }
            ]
        elif path.endswith("/commits"):
            yield [
                {
                    "sha": "c" * 40,
                    "author": {"login": "alice"},
                    "commit": {
                        "message": "feat: login\n\nbody",
                        "author": {"name": "Alice", "date": "2026-10-02T00:00:00Z"},
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
