"""Offline fixtures for rule tests (no network access, see tests/mocks/)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from app.services.rules import (
    IssueMeta,
    ItemState,
    PullRequestMeta,
    RepositorySnapshot,
)

MOCKS_DIR = Path(__file__).resolve().parents[1] / "mocks"


def _load(name: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((MOCKS_DIR / name).read_text(encoding="utf-8"))
    return data


@pytest.fixture
def now() -> datetime:
    return datetime.fromisoformat(_load("rules_snapshot.json")["now"])


@pytest.fixture
def snapshot() -> RepositorySnapshot:
    raw = _load("rules_snapshot.json")
    return RepositorySnapshot(
        pull_requests=tuple(
            PullRequestMeta(
                number=pr["number"],
                state=ItemState(pr["state"]),
                last_activity_at=datetime.fromisoformat(pr["last_activity_at"]),
                is_draft=pr["is_draft"],
            )
            for pr in raw["pull_requests"]
        ),
        issues=tuple(
            IssueMeta(
                number=i["number"],
                state=ItemState(i["state"]),
                last_activity_at=datetime.fromisoformat(i["last_activity_at"]),
            )
            for i in raw["issues"]
        ),
    )
