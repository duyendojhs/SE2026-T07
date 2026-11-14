"""Mocked concurrent retry harness; not a production throughput benchmark."""

from __future__ import annotations

import json
import math
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import httpx

from app.github.app_auth import GitHubAPIError
from app.github.client import GitHubClient

TASK_COUNT = 100
MAX_RETRIES = 2
REPO_PATH = "/repos/duyendojhs/SE2026-T07"


def _nearest_rank(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(percentile * len(ordered)) - 1)]


def _run_task(task_id: int) -> tuple[float, str, int]:
    """Run one task with entirely task-local transport and call state."""
    calls = 0
    persistent_failure = task_id % 20 == 0
    one_transient_failure = task_id % 10 == 0 and not persistent_failure

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if persistent_failure or (one_transient_failure and calls == 1):
            return httpx.Response(503, json={"message": "mock transient failure"})
        return httpx.Response(200, json={"ok": True, "task_id": task_id})

    client = GitHubClient(
        token_provider=lambda: "mock-token",
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
        sleep=lambda _: None,
        max_retries=MAX_RETRIES,
    )
    started = time.perf_counter()
    try:
        client.get_json(REPO_PATH)
    except GitHubAPIError:
        outcome = "exhausted"
    else:
        outcome = "success"
    finally:
        elapsed_ms = (time.perf_counter() - started) * 1000
        client.close()
    return elapsed_ms, outcome, calls


def main() -> None:
    with ThreadPoolExecutor(max_workers=TASK_COUNT) as executor:
        results = list(executor.map(_run_task, range(TASK_COUNT)))

    latencies = [latency for latency, _, _ in results]
    outcomes = [outcome for _, outcome, _ in results]
    report: dict[str, Any] = {
        "harness": "mocked GitHubClient calls; no network or database",
        "tasks": TASK_COUNT,
        "workers": TASK_COUNT,
        "max_retries": MAX_RETRIES,
        "results": {
            "success": outcomes.count("success"),
            "exhausted": outcomes.count("exhausted"),
            "attempts_total": sum(attempts for _, _, attempts in results),
        },
        "latency_ms": {
            "p50": round(_nearest_rank(latencies, 0.50), 3),
            "p95": round(_nearest_rank(latencies, 0.95), 3),
            "max": round(max(latencies), 3),
            "method": "nearest-rank percentile over per-task perf_counter durations",
        },
        "state_isolation": "each worker owns its client, MockTransport, and attempt counter",
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
