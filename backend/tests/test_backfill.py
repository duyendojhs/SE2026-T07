from collections.abc import Iterator
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy import event as sqlalchemy_event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

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
    assert len(session.exec(select(PullRequest)).all()) == 1


class GeneratedIssueClient:
    def __init__(self, issues: list[dict[str, Any]]) -> None:
        self.issues = issues

    def paginate(
        self, path: str, *, params: dict[str, Any] | None = None
    ) -> Iterator[list[dict[str, Any]]]:
        if path.endswith("/issues"):
            yield self.issues
        else:
            yield []


def _generated_issue(github_id: int) -> dict[str, Any]:
    return {
        "id": github_id,
        "number": github_id,
        "title": f"Issue {github_id}",
        "state": "open",
        "user": {"login": "alice"},
        "assignees": [],
        "labels": [],
        "created_at": "2026-10-01T00:00:00Z",
        "updated_at": "2026-10-02T00:00:00Z",
    }


@given(github_ids=st.lists(st.integers(min_value=1, max_value=100_000), max_size=8))
@settings(max_examples=30, derandomize=True, database=None)
def test_generated_duplicate_issue_ids_remain_unique_after_reordered_reingestion(
    github_ids: list[int],
) -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    try:
        with Session(engine) as isolated_session:
            tenant = Tenant(slug="property-backfill", name="Property Backfill")
            isolated_session.add(tenant)
            isolated_session.commit()
            repository = Repository(
                tenant_id=tenant.id,
                github_id=101,
                full_name="duyendojhs/property-backfill",
            )
            isolated_session.add(repository)
            isolated_session.commit()

            issues = [_generated_issue(github_id) for github_id in github_ids]
            expected_ids = set(github_ids)
            first = BackfillService(
                isolated_session,
                GeneratedIssueClient(issues),
                tenant_id=tenant.id,
                repo=repository,
            ).run(days=1)
            assert first.status == "ready"
            first_ids = {
                issue.github_id for issue in isolated_session.exec(select(Issue)).all()
            }
            assert first_ids == expected_ids

            second = BackfillService(
                isolated_session,
                GeneratedIssueClient(list(reversed(issues))),
                tenant_id=tenant.id,
                repo=repository,
            ).run(days=1)
            second_ids = {
                issue.github_id for issue in isolated_session.exec(select(Issue)).all()
            }
            assert second.status == "ready"
            assert second_ids == expected_ids
            assert len(isolated_session.exec(select(Issue)).all()) == len(expected_ids)
    finally:
        SQLModel.metadata.drop_all(engine)
        engine.dispose()


def test_commit_failure_never_returns_success_and_recovery_is_consistent(
    session: Session,
) -> None:
    tenant, repo = _seed(session)

    def fail_commit(_: Session) -> None:
        raise SQLAlchemyError("injected commit failure")

    sqlalchemy_event.listen(session, "before_commit", fail_commit)
    try:
        with pytest.raises(SQLAlchemyError, match="injected commit failure"):
            BackfillService(
                session,
                FakeGitHubClient(),
                tenant_id=tenant.id,
                repo=repo,
            ).run()
    finally:
        sqlalchemy_event.remove(session, "before_commit", fail_commit)
        session.rollback()

    assert session.exec(select(Issue)).all() == []
    assert session.exec(select(PullRequest)).all() == []

    recovered = BackfillService(
        session,
        FakeGitHubClient(),
        tenant_id=tenant.id,
        repo=repo,
    ).run()
    assert recovered.status == "ready"
    assert len(session.exec(select(Issue)).all()) == 1
    assert len(session.exec(select(PullRequest)).all()) == 1
