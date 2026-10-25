import json
from pathlib import Path
from typing import Any

FORBIDDEN_KEYS = {
    "patch",
    "diff",
    "blob",
    "content",
    "raw_content",
    "file_content",
    "body",
    "commit_body",
    "comment_body",
}


def collect_keys(value: Any) -> set[str]:
    """Collect every dictionary key recursively."""

    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(key)
            keys.update(collect_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(collect_keys(child))
    return keys


def test_fixture_contains_no_forbidden_payload() -> None:
    fixture = Path(__file__).parent / "fixtures" / "github_metadata.json"
    payload = json.loads(fixture.read_text(encoding="utf-8"))

    forbidden = FORBIDDEN_KEYS.intersection(collect_keys(payload))

    assert forbidden == set(), f"forbidden fixture keys: {sorted(forbidden)}"
