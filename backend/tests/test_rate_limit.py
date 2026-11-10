import httpx
import pytest

from app.github.allowed_endpoints import EndpointNotAllowed
from app.github.app_auth import GitHubAPIError
from app.github.client import GitHubClient


def test_rate_limit_retry_after_is_respected() -> None:
    calls = 0
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        assert request.headers["Authorization"].startswith("Bearer ")
        if calls == 1:
            return httpx.Response(
                403,
                headers={"Retry-After": "1"},
                json={"message": "secondary rate limit"},
            )
        return httpx.Response(200, json={"full_name": "duyendojhs/SE2026-T07"})

    client = GitHubClient(
        token_provider=lambda: "installation-token",
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
        sleep=sleeps.append,
    )
    payload, _ = client.get_json("/repos/duyendojhs/SE2026-T07")

    assert payload["full_name"] == "duyendojhs/SE2026-T07"
    assert calls == 2
    assert sleeps == [1.0]
    client.close()


def test_rate_limit_exhaustion_raises() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(403, headers={"Retry-After": "0"}, json={"message": "limited"})

    client = GitHubClient(
        token_provider=lambda: "token",
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
        sleep=lambda _: None,
        max_retries=1,
    )
    with pytest.raises(GitHubAPIError):
        client.get_json("/repos/duyendojhs/SE2026-T07")
    client.close()


def test_bad_token_is_not_retried() -> None:
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(401, json={"message": "bad credentials"})

    client = GitHubClient(
        token_provider=lambda: "token",
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
        sleep=lambda _: None,
    )
    with pytest.raises(GitHubAPIError):
        client.get_json("/repos/duyendojhs/SE2026-T07")
    assert calls == 1
    client.close()


def test_content_endpoint_is_blocked_before_network() -> None:
    def handler(_: httpx.Request) -> httpx.Response:  # pragma: no cover - must not run
        raise AssertionError("network should not be called")

    client = GitHubClient(
        token_provider=lambda: "token",
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )
    with pytest.raises(EndpointNotAllowed):
        client.get_json("/repos/duyendojhs/SE2026-T07/contents/app.py")
    client.close()


def test_pagination_follows_link_header() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.params.get("page") == "2":
            return httpx.Response(200, json=[{"id": 2}])
        return httpx.Response(
            200,
            json=[{"id": 1}],
            headers={
                "Link": (
                    '<https://api.github.com/repos/duyendojhs/SE2026-T07/issues?page=2>; '
                    'rel="next"'
                )
            },
        )

    client = GitHubClient(
        token_provider=lambda: "token",
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )
    pages = list(client.paginate("/repos/duyendojhs/SE2026-T07/issues"))

    assert pages == [[{"id": 1}], [{"id": 2}]]
    client.close()
