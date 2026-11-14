import httpx
import pytest
from hypothesis import given, settings, strategies as st

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


def test_http_500_is_retried_then_succeeds() -> None:
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(500, json={"message": "temporary server failure"})
        return httpx.Response(200, json={"ok": True})

    client = GitHubClient(
        token_provider=lambda: "token",
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
        sleep=lambda _: None,
    )
    try:
        payload, _ = client.get_json("/repos/duyendojhs/SE2026-T07")
        assert payload == {"ok": True}
        assert calls == 2
    finally:
        client.close()


def test_read_timeout_is_retried_then_succeeds() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.ReadTimeout("temporary timeout", request=request)
        return httpx.Response(200, json={"full_name": "duyendojhs/SE2026-T07"})

    client = GitHubClient(
        token_provider=lambda: "token",
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
        sleep=lambda _: None,
    )
    try:
        payload, _ = client.get_json("/repos/duyendojhs/SE2026-T07")
        assert payload["full_name"] == "duyendojhs/SE2026-T07"
        assert calls == 2
    finally:
        client.close()


def test_connection_error_is_retried_then_succeeds() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.ConnectError("temporary connection error", request=request)
        return httpx.Response(200, json={"full_name": "duyendojhs/SE2026-T07"})

    client = GitHubClient(
        token_provider=lambda: "token",
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
        sleep=lambda _: None,
    )
    try:
        payload, _ = client.get_json("/repos/duyendojhs/SE2026-T07")
        assert payload["full_name"] == "duyendojhs/SE2026-T07"
        assert calls == 2
    finally:
        client.close()


def test_transient_http_error_on_post_is_not_retried() -> None:
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(500, json={"message": "temporary server failure"})

    client = GitHubClient(
        token_provider=lambda: "token",
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
        sleep=lambda _: None,
    )
    try:
        with pytest.raises(GitHubAPIError):
            client.request("POST", "/repos/duyendojhs/SE2026-T07")
        assert calls == 1
    finally:
        client.close()


@given(
    max_retries=st.integers(min_value=0, max_value=5),
    transient_failures=st.lists(
        st.sampled_from(["timeout", "connect"]), max_size=8
    ),
)
@settings(max_examples=40, derandomize=True, database=None)
def test_timeout_retry_is_bounded_and_returns_only_after_success(
    max_retries: int, transient_failures: list[str]
) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls <= len(transient_failures):
            failure = transient_failures[calls - 1]
            if failure == "timeout":
                raise httpx.ReadTimeout("temporary timeout", request=request)
            raise httpx.ConnectError("temporary connection error", request=request)
        return httpx.Response(200, json={"ok": True})

    client = GitHubClient(
        token_provider=lambda: "token",
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
        sleep=lambda _: None,
        max_retries=max_retries,
    )
    try:
        if len(transient_failures) <= max_retries:
            payload, _ = client.get_json("/repos/duyendojhs/SE2026-T07")
            assert payload == {"ok": True}
            assert calls == len(transient_failures) + 1
        else:
            with pytest.raises(GitHubAPIError):
                client.get_json("/repos/duyendojhs/SE2026-T07")
            assert calls == max_retries + 1
    finally:
        client.close()
