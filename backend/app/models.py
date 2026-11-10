"""SQLModel tables for the S1 metadata ingestion slice."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from datetime import date as date_type
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

JSON_TYPE = JSON().with_variant(JSONB(), "postgresql")


def utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(UTC)


def created_at_column() -> Column[datetime]:
    """Timestamp column with a Python-side UTC default."""

    return Column(DateTime(timezone=True), nullable=False, default=utcnow)


class Tenant(SQLModel, table=True):
    __tablename__ = "tenants"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    slug: str = Field(index=True, unique=True, max_length=80)
    name: str = Field(max_length=200)
    timezone: str = Field(default="Asia/Ho_Chi_Minh", max_length=64)
    created_at: datetime = Field(default_factory=utcnow, sa_column=created_at_column())
    deleted_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )


class Installation(SQLModel, table=True):
    __tablename__ = "installations"
    __table_args__ = (UniqueConstraint("installation_id"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True)
    installation_id: int = Field(index=True)
    account_login: str = Field(max_length=200)
    suspended: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utcnow, sa_column=created_at_column())


class Repository(SQLModel, table=True):
    __tablename__ = "repositories"
    __table_args__ = (
        UniqueConstraint("tenant_id", "github_id"),
        Index("ix_repositories_tenant_full_name", "tenant_id", "full_name"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True)
    installation_id: uuid.UUID | None = Field(
        default=None, foreign_key="installations.id", index=True
    )
    github_id: int
    full_name: str = Field(max_length=300)
    default_branch: str = Field(default="main", max_length=200)
    private: bool = Field(default=False)
    connected_at: datetime = Field(default_factory=utcnow, sa_column=created_at_column())
    last_synced_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    sync_status: str = Field(default="pending", max_length=20)
    sync_error: str | None = Field(
        default=None, sa_column=Column(String(1000), nullable=True)
    )


class Member(SQLModel, table=True):
    __tablename__ = "members"
    __table_args__ = (UniqueConstraint("tenant_id", "github_id"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True)
    github_id: int
    login: str = Field(max_length=200)
    display_name: str | None = Field(default=None, max_length=200)
    role: str = Field(default="member", max_length=20)
    timezone: str = Field(default="Asia/Ho_Chi_Minh", max_length=64)
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utcnow, sa_column=created_at_column())


class RawEvent(SQLModel, table=True):
    __tablename__ = "raw_events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True)
    repo_id: uuid.UUID | None = Field(
        default=None, foreign_key="repositories.id", index=True
    )
    delivery_id: str | None = Field(default=None, max_length=200)
    event_type: str = Field(max_length=100)
    payload_json: dict[str, Any] = Field(sa_column=Column(JSON_TYPE, nullable=False))
    payload_hash: str = Field(max_length=64)
    received_at: datetime = Field(default_factory=utcnow, sa_column=created_at_column())
    processed_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )


class Issue(SQLModel, table=True):
    __tablename__ = "issues"
    __table_args__ = (
        UniqueConstraint("repo_id", "github_id"),
        Index("ix_issues_tenant_state_updated", "tenant_id", "state", "updated_at"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True)
    repo_id: uuid.UUID = Field(foreign_key="repositories.id", index=True)
    github_id: int
    number: int
    title: str = Field(max_length=500)
    state: str = Field(max_length=20)
    author_login: str | None = Field(default=None, max_length=200)
    assignee_logins: list[str] = Field(
        default_factory=list, sa_column=Column(JSON_TYPE, nullable=False)
    )
    labels: list[str] = Field(
        default_factory=list, sa_column=Column(JSON_TYPE, nullable=False)
    )
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    closed_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    is_stale: bool = Field(default=False)


class PullRequest(SQLModel, table=True):
    __tablename__ = "pull_requests"
    __table_args__ = (
        UniqueConstraint("repo_id", "github_id"),
        Index(
            "ix_pull_requests_tenant_state_created",
            "tenant_id",
            "state",
            "created_at",
        ),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True)
    repo_id: uuid.UUID = Field(foreign_key="repositories.id", index=True)
    github_id: int
    number: int
    title: str = Field(max_length=500)
    state: str = Field(max_length=20)
    author_login: str | None = Field(default=None, max_length=200)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    merged_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    closed_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    is_draft: bool = Field(default=False)
    additions: int = Field(default=0)
    deletions: int = Field(default=0)
    changed_files: int = Field(default=0)
    base_branch: str | None = Field(default=None, max_length=200)
    head_sha: str | None = Field(default=None, max_length=64)
    merge_commit_sha: str | None = Field(default=None, max_length=64)


class Review(SQLModel, table=True):
    __tablename__ = "pr_reviews"
    __table_args__ = (
        UniqueConstraint("pr_id", "github_id"),
        Index("ix_pr_reviews_pr_submitted", "pr_id", "submitted_at"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True)
    pr_id: uuid.UUID = Field(foreign_key="pull_requests.id", index=True)
    github_id: int
    reviewer_login: str | None = Field(default=None, max_length=200)
    state: str = Field(max_length=50)
    submitted_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )


class Comment(SQLModel, table=True):
    __tablename__ = "comments"
    __table_args__ = (
        UniqueConstraint("repo_id", "github_id"),
        Index(
            "ix_comments_tenant_parent_created",
            "tenant_id",
            "parent_type",
            "parent_id",
            "created_at",
        ),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True)
    repo_id: uuid.UUID = Field(foreign_key="repositories.id", index=True)
    github_id: int
    parent_type: str = Field(max_length=20)
    parent_id: int
    author_login: str | None = Field(default=None, max_length=200)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    body_length: int = Field(default=0)
    has_code_block: bool = Field(default=False)


class Commit(SQLModel, table=True):
    __tablename__ = "commits"
    __table_args__ = (
        UniqueConstraint("repo_id", "sha"),
        Index("ix_commits_tenant_committed", "tenant_id", "committed_at"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True)
    repo_id: uuid.UUID = Field(foreign_key="repositories.id", index=True)
    sha: str = Field(max_length=64)
    author_login: str | None = Field(default=None, max_length=200)
    committed_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    message_subject: str = Field(default="", max_length=200)
    pr_id: uuid.UUID | None = Field(
        default=None, foreign_key="pull_requests.id", index=True
    )


class SyncCursor(SQLModel, table=True):
    __tablename__ = "sync_cursors"
    __table_args__ = (UniqueConstraint("repo_id", "resource"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    repo_id: uuid.UUID = Field(foreign_key="repositories.id", index=True)
    resource: str = Field(max_length=50)
    cursor: str | None = Field(default=None, max_length=1000)
    etag: str | None = Field(default=None, max_length=500)
    last_synced_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )


class ProcessedDelivery(SQLModel, table=True):
    __tablename__ = "processed_deliveries"

    delivery_id: str = Field(primary_key=True, max_length=200)
    received_at: datetime = Field(default_factory=utcnow, sa_column=created_at_column())


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_tenant_created", "tenant_id", "created_at"),
        UniqueConstraint("tenant_id", "prev_hash"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True)
    actor_hash: str = Field(max_length=64)
    action: str = Field(max_length=100)
    resource: str = Field(max_length=500)
    request_hash: str = Field(max_length=64)
    prev_hash: str = Field(max_length=64)
    entry_hash: str = Field(max_length=64, unique=True)
    created_at: datetime = Field(default_factory=utcnow, sa_column=created_at_column())


class AuditCheckpoint(SQLModel, table=True):
    __tablename__ = "audit_checkpoints"
    __table_args__ = (UniqueConstraint("tenant_id", "upto_entry_id"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True)
    upto_entry_id: uuid.UUID = Field(foreign_key="audit_logs.id", index=True)
    hash: str = Field(max_length=64)
    created_at: datetime = Field(default_factory=utcnow, sa_column=created_at_column())


class MetricDaily(SQLModel, table=True):
    __tablename__ = "metrics_daily"
    __table_args__ = (UniqueConstraint("tenant_id", "date", "metric_key"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True)
    date: date_type = Field(index=True)
    metric_key: str = Field(max_length=100)
    value: float
    sample_size: int = Field(default=0)
    confidence: str | None = Field(default=None, max_length=20)
    meta_json: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON_TYPE, nullable=False)
    )


class Finding(SQLModel, table=True):
    __tablename__ = "findings"
    __table_args__ = (
        UniqueConstraint("tenant_id", "dedupe_key"),
        Index("ix_findings_tenant_status_priority", "tenant_id", "status", "priority_score"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True)
    repo_id: uuid.UUID = Field(foreign_key="repositories.id", index=True)
    rule_id: str = Field(max_length=100)
    rule_version: int = Field(default=1)
    severity: str = Field(max_length=20)
    confidence: str = Field(max_length=20)
    priority_score: float = Field(default=0.0)
    status: str = Field(default="open", max_length=20)
    title: str = Field(max_length=300)
    description: str = Field(default="", max_length=2000)
    evidence_json: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON_TYPE, nullable=False)
    )
    metrics_json: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON_TYPE, nullable=False)
    )
    dedupe_key: str = Field(max_length=300)
    detected_at: datetime = Field(default_factory=utcnow, sa_column=created_at_column())
    resolved_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )


class Agreement(SQLModel, table=True):
    __tablename__ = "agreements"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True)
    name: str = Field(max_length=200)
    metric_key: str = Field(max_length=100)
    comparator: str = Field(max_length=20)
    target: float
    active_from: date_type
    active_to: date_type | None = Field(default=None)
    created_by: uuid.UUID | None = Field(default=None, foreign_key="members.id")


class Intervention(SQLModel, table=True):
    __tablename__ = "interventions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True)
    finding_id: uuid.UUID | None = Field(default=None, foreign_key="findings.id")
    action: str = Field(max_length=500)
    owner: uuid.UUID | None = Field(default=None, foreign_key="members.id")
    planned_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    expected_effect: str | None = Field(default=None, max_length=500)
    measured_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    actual_effect: str | None = Field(default=None, max_length=500)
    notes: str | None = Field(default=None, max_length=2000)


class PulseResponse(SQLModel, table=True):
    __tablename__ = "pulse_responses"
    __table_args__ = (UniqueConstraint("tenant_id", "week_start", "respondent_key"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True)
    week_start: date_type
    respondent_key: str = Field(max_length=64)
    satisfaction: int
    learning: int
    support: int
    created_at: datetime = Field(default_factory=utcnow, sa_column=created_at_column())


class Summary(SQLModel, table=True):
    __tablename__ = "summaries"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True)
    period_start: date_type
    period_end: date_type
    model: str = Field(max_length=100)
    prompt_version: str = Field(max_length=50)
    facts_hash: str = Field(max_length=64)
    content: str = Field(max_length=10000)
    citations_json: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON_TYPE, nullable=False)
    )
    created_at: datetime = Field(default_factory=utcnow, sa_column=created_at_column())


