"""Rule engine abstractions: ``Severity``, ``RuleFinding`` and ``BaseRule``."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import ClassVar

from app.services.rules.models import RepositorySnapshot, require_aware


class Severity(StrEnum):
    """Categorical severity. Deterministic per rule; never a numeric score."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class RuleFinding:
    """Structured, explainable finding at team/module level.

    Attributes:
        rule_id: Stable identifier of the rule that produced the finding.
        severity: Categorical severity.
        title: Short human-readable summary.
        trigger_reason: Explicit explanation of why the rule fired.
        impacted_items: Identifiers of affected items (e.g. ``"PR #12"``).
        metrics: Raw measurements backing the reason, for auditability.
    """

    rule_id: str
    severity: Severity
    title: str
    trigger_reason: str
    impacted_items: tuple[str, ...]
    metrics: Mapping[str, int | float | str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.rule_id.strip():
            raise ValueError("rule_id must not be empty")
        if not self.trigger_reason.strip():
            raise ValueError("trigger_reason must not be empty")


class BaseRule(ABC):
    """Abstract base for all rules.

    Subclasses set ``rule_id`` / ``title`` and implement ``_evaluate``. Rules are
    pure and deterministic: the clock is injected via ``now``, never read.
    """

    rule_id: ClassVar[str]
    title: ClassVar[str]

    def __init__(self) -> None:
        if not getattr(type(self), "rule_id", "") or not getattr(type(self), "title", ""):
            raise TypeError(f"{type(self).__name__} must define rule_id and title")

    def evaluate(self, snapshot: RepositorySnapshot, now: datetime) -> list[RuleFinding]:
        """Evaluate the rule; returns an empty list when nothing triggers."""
        require_aware(now, "now")
        return self._evaluate(snapshot, now)

    @abstractmethod
    def _evaluate(self, snapshot: RepositorySnapshot, now: datetime) -> list[RuleFinding]:
        """Rule-specific logic; ``now`` is guaranteed timezone-aware."""
