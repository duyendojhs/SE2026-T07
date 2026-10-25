import uuid

from app.ingestion.normalizer import (
    normalize_comment,
    normalize_commit,
    normalize_issue,
    normalize_pull_request,
    normalize_review,
)


def test_issue_normalisation_keeps_metadata_only() -> None:
    tenant_id = uuid.uuid4()
    repo_id = uuid.uuid4()
    payload = {
        "id": 1001,
        "number": 7,
        "title": "Bug",
        "body": "do not keep me",
        "state": "open",
        "user": {"login": "alice"},
        "assignees": [{"login": "bob"}],
        "labels": [{"name": "bug"}],
        "created_at": "2026-10-01T00:00:00Z",
        "updated_at": "2026-10-02T00:00:00Z",
        "closed_at": None,
    }

    data = normalize_issue(payload, tenant_id=tenant_id, repo_id=repo_id)

    assert data["github_id"] == 1001
    assert data["number"] == 7
    assert data["author_login"] == "alice"
    assert data["assignee_logins"] == ["bob"]
    assert data["labels"] == ["bug"]
    assert "body" not in data


def test_pull_request_normalisation_detects_merged_state() -> None:
    data = normalize_pull_request(
        {
            "id": 11,
            "number": 12,
            "title": "Feature",
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
        },
        tenant_id=uuid.uuid4(),
        repo_id=uuid.uuid4(),
    )

    assert data["state"] == "merged"
    assert data["base_branch"] == "main"
    assert data["merge_commit_sha"] == "b" * 40


def test_review_and_comment_normalisation() -> None:
    tenant_id = uuid.uuid4()
    repo_id = uuid.uuid4()
    pr_id = uuid.uuid4()

    review = normalize_review(
        {
            "id": 201,
            "user": {"login": "reviewer"},
            "state": "APPROVED",
            "submitted_at": "2026-10-02T00:00:00Z",
        },
        tenant_id=tenant_id,
        pr_id=pr_id,
    )
    comment = normalize_comment(
        {
            "id": 301,
            "user": {"login": "commenter"},
            "body": "line\n```\ncode\n```",
            "created_at": "2026-10-02T00:00:00Z",
            "updated_at": "2026-10-02T00:00:00Z",
        },
        tenant_id=tenant_id,
        repo_id=repo_id,
        parent_type="pr",
        parent_id=12,
    )

    assert review["state"] == "APPROVED"
    assert comment["body_length"] > 0
    assert comment["has_code_block"] is True
    assert "body" not in comment


def test_commit_normalisation_keeps_only_subject() -> None:
    data = normalize_commit(
        {
            "sha": "c" * 40,
            "author": {"login": "alice"},
            "commit": {
                "message": "feat: add login\n\nlong body",
                "author": {"name": "Alice", "date": "2026-10-02T00:00:00Z"},
            },
        },
        tenant_id=uuid.uuid4(),
        repo_id=uuid.uuid4(),
    )

    assert data["message_subject"] == "feat: add login"
    assert "message" not in data
    assert data["author_login"] == "alice"
