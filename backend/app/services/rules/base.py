from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class RuleFinding:
    """Explainable output for a single rule evaluation."""

    rule_id: str
    severity: str
    title: str
    trigger_reason: str
    impacted_items: list[str] = field(default_factory=list)


class BaseRule(ABC):
    """Abstract base class for deterministic rule checks."""

    rule_id: str = "base-rule"
    severity: str = "warning"
    title: str = "Base rule"

    def __call__(
        self,
        items: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None,
    ) -> list[RuleFinding]:
        return self.evaluate(items)

    @abstractmethod
    def evaluate(
        self,
        items: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None,
    ) -> list[RuleFinding]:
        """Evaluate items and return zero or more findings."""
