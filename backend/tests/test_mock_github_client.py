from pathlib import Path
from typing import Any

import httpx
import pytest

from mocks.mock_github_client import MockGitHubClient


REPOSITORY = "/repos/example/project"


def _retrieve(client: MockGitHubClient, path: str) -> list[dict[str, Any]]:
    return [item for page in client.paginate(path) for item in page]


def test_mock_client_retrieves_all_fixture_types_offline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reject_http_request(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("MockGitHubClient must not make HTTP requests")

    monkeypatch.setattr(httpx.Client, "request", reject_http_request)
    client = MockGitHubClient()

    pull_requests = _retrieve(client, f"{REPOSITORY}/pulls")
    issues = _retrieve(client, f"{REPOSITORY}/issues")
    commits = _retrieve(client, f"{REPOSITORY}/commits")
    reviews = _retrieve(client, f"{REPOSITORY}/pulls/61/reviews")

    assert {pull_request["state"] for pull_request in pull_requests} == {"open", "closed"}
    assert {review["state"] for review in reviews} == {"CHANGES_REQUESTED", "COMMENTED"}
    assert any(issue["assignees"] for issue in issues)
    assert any(not issue["assignees"] for issue in issues)
    assert all("author" in commit and "commit" in commit for commit in commits)
    assert all("date" in commit["commit"]["author"] for commit in commits)
    client.close()


def test_mock_client_returns_independent_data_and_rejects_unknown_endpoint() -> None:
    client = MockGitHubClient()
    first_page = next(client.paginate(f"{REPOSITORY}/issues"))
    first_page[0]["state"] = "changed-by-test"

    next_page = next(client.paginate(f"{REPOSITORY}/issues"))
    assert next_page[0]["state"] == "open"

    with pytest.raises(ValueError, match="Unsupported mock GitHub endpoint"):
        list(client.paginate(f"{REPOSITORY}/contents"))


def test_mock_client_loads_fixtures_from_custom_directory(tmp_path: Path) -> None:
    source = Path(__file__).parent / "mocks"
    for filename in ("prs_mock.json", "issues_mock.json", "commits_mock.json"):
        (tmp_path / filename).write_text(
            (source / filename).read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    client = MockGitHubClient(tmp_path)
    assert _retrieve(client, f"{REPOSITORY}/pulls")
