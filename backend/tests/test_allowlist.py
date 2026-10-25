import pytest

from app.github.allowed_endpoints import (
    EndpointNotAllowed,
    assert_allowed,
    comment_metadata,
    is_allowed,
    strip_payload,
)


def test_metadata_endpoints_are_allowed() -> None:
    assert_allowed("/repos/duyendojhs/SE2026-T07")
    assert_allowed("/repos/duyendojhs/SE2026-T07/issues?state=all")
    assert_allowed("/repos/duyendojhs/SE2026-T07/pulls/12/reviews")
    assert_allowed("https://api.github.com/repos/duyendojhs/SE2026-T07/commits?per_page=100")


@pytest.mark.parametrize(
    "path",
    [
        "/repos/duyendojhs/SE2026-T07/contents/src/main.py",
        "/repos/duyendojhs/SE2026-T07/git/blobs/abc",
        "/repos/duyendojhs/SE2026-T07/compare/main...feature",
        "/repos/duyendojhs/SE2026-T07/pulls/12/files",
        "/repos/duyendojhs/SE2026-T07/actions/runs",
        "/repos/duyendojhs/SE2026-T07/unknown",
    ],
)
def test_content_and_unknown_endpoints_are_rejected(path: str) -> None:
    assert not is_allowed(path)
    with pytest.raises(EndpointNotAllowed):
        assert_allowed(path)


def test_strip_payload_removes_code_and_comment_content() -> None:
    payload = {
        "title": "metadata only",
        "body": "comment body",
        "patch": "@@ -1 +1 @@",
        "Authorization": "Bearer secret-token",
        "nested": {
            "diff": "secret",
            "keep": 1,
            "message": "commit body",
            "token": "secret-token",
        },
    }

    clean, stripped = strip_payload(payload)

    assert stripped == 6
    assert clean == {"title": "metadata only", "nested": {"keep": 1}}
    assert "body" not in clean
    assert "Authorization" not in clean


def test_comment_metadata_does_not_return_body() -> None:
    length, has_code = comment_metadata({"body": "hello\n```python\nprint(1)\n```"})

    assert length > 10
    assert has_code is True
