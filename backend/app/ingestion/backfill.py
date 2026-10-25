"""90-day metadata backfill with idempotent upserts."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlmodel import Session, select

from app.audit.service import AuditService
from app.core.config import settings
from app.github.allowed_endpoints import strip_payload
from app.ingestion.normalizer import (
    normalize_comment,
    normalize_commit,
    normalize_issue,
    normalize_pull_request,
    normalize_review,
)
from app.models import (
    Comment,
    Commit,
    Issue,
    PullRequest,
    RawEvent,
    Repository,
    Review,
    SyncCursor,
    utcnow,
)


@dataclass
class BackfillResult:
    status: str
    counts: dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class BackfillService:
    """Fetch metadata pages and persist them without content payloads."""

    def __init__(
        self,
        session: Session,
        client: Any,
        *,
        tenant_id: uuid.UUID,
        repo: Repository,
        audit: AuditService | None = None,
    ) -> None:
        self.session = session
        self.client = client
        self.tenant_id = tenant_id
        self.repo = repo
        self.audit = audit or AuditService()
        self.counts: dict[str, int] = {
            "issues": 0,
            "pull_requests": 0,
            "reviews": 0,
            "comments": 0,
            "commits": 0,
        }
        self.errors: list[str] = []

    def run(self, *, days: int | None = None) -> BackfillResult:
        since = utcnow() - timedelta(days=days or settings.backfill_days)
        self.repo.sync_status = "syncing"
        self.repo.sync_error = None
        self.session.add(self.repo)
        self.session.flush()

        issue_numbers: set[int] = set()
        pr_numbers: set[int] = set()

        try:
            issue_numbers = self._ingest_issues(since)
        except Exception as exc:  # noqa: BLE001 - isolate partial failures
            self.errors.append(f"issues: {type(exc).__name__}")

        try:
            pr_numbers = self._ingest_pull_requests(since)
        except Exception as exc:  # noqa: BLE001 - isolate partial failures
            self.errors.append(f"pull_requests: {type(exc).__name__}")

        for number in sorted(issue_numbers | pr_numbers):
            try:
                self._ingest_reviews(number) if number in pr_numbers else None
                self._ingest_comments(number)
            except Exception as exc:  # noqa: BLE001 - isolate partial failures
                self.errors.append(f"comments/reviews {number}: {type(exc).__name__}")

        try:
            self._ingest_commits(since)
        except Exception as exc:  # noqa: BLE001 - isolate partial failures
            self.errors.append(f"commits: {type(exc).__name__}")

        self.repo.last_synced_at = utcnow()
        if self.errors and any(self.counts.values()):
            self.repo.sync_status = "partial"
            self.repo.sync_error = "; ".join(self.errors)[:1000]
        elif self.errors:
            self.repo.sync_status = "error"
            self.repo.sync_error = "; ".join(self.errors)[:1000]
        else:
            self.repo.sync_status = "ready"
            self.repo.sync_error = None
        self.session.add(self.repo)
        self.session.commit()
        return BackfillResult(status=self.repo.sync_status, counts=self.counts, errors=self.errors)

    def _ingest_issues(self, since: datetime) -> set[int]:
        numbers: set[int] = set()
        for page in self.client.paginate(
            f"/repos/{self.repo.full_name}/issues",
            params={
                "state": "all",
                "since": since.isoformat(),
                "per_page": 100,
                "sort": "updated",
                "direction": "desc",
            },
        ):
            for item in page:
                if item.get("pull_request"):
                    continue
                data = normalize_issue(item, tenant_id=self.tenant_id, repo_id=self.repo.id)
                self._upsert_issue(data)
                numbers.add(data["number"])
                self.counts["issues"] += 1
                self._store_raw_event("backfill.issue", item)
            self._audit("issues", len(page))
        self._touch_cursor("issues")
        return numbers

    def _ingest_pull_requests(self, since: datetime) -> set[int]:
        numbers: set[int] = set()
        for page in self.client.paginate(
            f"/repos/{self.repo.full_name}/pulls",
            params={
                "state": "all",
                "sort": "updated",
                "direction": "desc",
                "per_page": 100,
            },
        ):
            for item in page:
                updated = item.get("updated_at")
                if updated and _parse(updated) < since:
                    continue
                data = normalize_pull_request(
                    item, tenant_id=self.tenant_id, repo_id=self.repo.id
                )
                self._upsert_pull_request(data)
                numbers.add(data["number"])
                self.counts["pull_requests"] += 1
                self._store_raw_event("backfill.pull_request", item)
            self._audit("pull_requests", len(page))
        self._touch_cursor("pull_requests")
        return numbers

    def _ingest_reviews(self, number: int) -> None:
        for page in self.client.paginate(
            f"/repos/{self.repo.full_name}/pulls/{number}/reviews",
            params={"per_page": 100},
        ):
            pr = self._get_pr(number)
            if pr is None:
                return
            for item in page:
                data = normalize_review(item, tenant_id=self.tenant_id, pr_id=pr.id)
                self._upsert_review(data)
                self.counts["reviews"] += 1
                self._store_raw_event("backfill.review", item)

    def _ingest_comments(self, number: int) -> None:
        for page in self.client.paginate(
            f"/repos/{self.repo.full_name}/issues/{number}/comments",
            params={"per_page": 100},
        ):
            for item in page:
                data = normalize_comment(
                    item,
                    tenant_id=self.tenant_id,
                    repo_id=self.repo.id,
                    parent_type="pr" if self._get_pr(number) else "issue",
                    parent_id=number,
                )
                self._upsert_comment(data)
                self.counts["comments"] += 1
                self._store_raw_event("backfill.comment", item)

    def _ingest_commits(self, since: datetime) -> None:
        for page in self.client.paginate(
            f"/repos/{self.repo.full_name}/commits",
            params={"since": since.isoformat(), "per_page": 100},
        ):
            for item in page:
                data = normalize_commit(item, tenant_id=self.tenant_id, repo_id=self.repo.id)
                self._upsert_commit(data)
                self.counts["commits"] += 1
                self._store_raw_event("backfill.commit", item)
            self._audit("commits", len(page))
        self._touch_cursor("commits")

    def _upsert_issue(self, data: dict[str, Any]) -> Issue:
        return _upsert(
            self.session,
            Issue,
            Issue.repo_id == self.repo.id,
            Issue.github_id == data["github_id"],
            data=data,
        )

    def _upsert_pull_request(self, data: dict[str, Any]) -> PullRequest:
        return _upsert(
            self.session,
            PullRequest,
            PullRequest.repo_id == self.repo.id,
            PullRequest.github_id == data["github_id"],
            data=data,
        )

    def _upsert_review(self, data: dict[str, Any]) -> Review:
        return _upsert(
            self.session,
            Review,
            Review.pr_id == data["pr_id"],
            Review.github_id == data["github_id"],
            data=data,
        )

    def _upsert_comment(self, data: dict[str, Any]) -> Comment:
        return _upsert(
            self.session,
            Comment,
            Comment.repo_id == self.repo.id,
            Comment.github_id == data["github_id"],
            data=data,
        )

    def _upsert_commit(self, data: dict[str, Any]) -> Commit:
        return _upsert(
            self.session,
            Commit,
            Commit.repo_id == self.repo.id,
            Commit.sha == data["sha"],
            data=data,
        )

    def _get_pr(self, number: int) -> PullRequest | None:
        return self.session.exec(
            select(PullRequest).where(
                PullRequest.repo_id == self.repo.id,
                PullRequest.number == number,
            )
        ).first()

    def _store_raw_event(self, event_type: str, payload: dict[str, Any]) -> None:
        clean, _ = strip_payload(payload)
        encoded = json.dumps(clean, sort_keys=True, separators=(",", ":"), default=str)
        event = RawEvent(
            tenant_id=self.tenant_id,
            repo_id=self.repo.id,
            event_type=event_type,
            payload_json=clean,
            payload_hash=hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
        )
        self.session.add(event)

    def _audit(self, resource: str, count: int) -> None:
        self.audit.append(
            self.session,
            tenant_id=self.tenant_id,
            actor_id="system:backfill",
            action="github.backfill",
            resource=f"{self.repo.full_name}/{resource}",
            request_payload={"resource": resource, "page_items": count},
        )

    def _touch_cursor(self, resource: str) -> None:
        cursor = self.session.exec(
            select(SyncCursor).where(
                SyncCursor.repo_id == self.repo.id,
                SyncCursor.resource == resource,
            )
        ).first()
        if cursor is None:
            cursor = SyncCursor(repo_id=self.repo.id, resource=resource)
        cursor.cursor = None
        cursor.last_synced_at = utcnow()
        self.session.add(cursor)


def _parse(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _upsert(session: Session, model: Any, *conditions: Any, data: dict[str, Any]) -> Any:
    existing = session.exec(select(model).where(*conditions)).first()
    if existing is None:
        existing = model(**data)
        session.add(existing)
        session.flush()
        return existing
    for key, value in data.items():
        setattr(existing, key, value)
    session.add(existing)
    session.flush()
    return existing


