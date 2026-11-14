"""Offline concurrent harness for the local Issue-title undo API route."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import platform
import sys
import tempfile
import time
import uuid
from collections import Counter
from collections.abc import Generator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

os.environ["DATABASE_URL"] = "sqlite://"

import httpx
from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine, select

from app import models  # noqa: F401  # register SQLModel tables
from app.api.deps import get_session
from app.auth.session import SessionData, create_session_token
from app.main import app
from app.models import Issue, Repository, Tenant


@dataclass(frozen=True)
class UndoCase:
    slug: str
    repo_id: uuid.UUID
    issue_id: uuid.UUID
    sync_id: uuid.UUID
    owner_cookie: str


def _seed(engine: Any, count: int) -> list[UndoCase]:
    now = datetime.now(UTC)
    cases: list[UndoCase] = []
    with Session(engine) as session:
        for index in range(count):
            slug = f"undo-load-{index}"
            tenant = Tenant(slug=slug, name=f"Synthetic tenant {index}")
            repo = Repository(
                tenant_id=tenant.id,
                github_id=10_000 + index,
                full_name=f"synthetic/repo-{index}",
            )
            sync_id = uuid.uuid4()
            issue = Issue(
                tenant_id=tenant.id,
                repo_id=repo.id,
                github_id=20_000 + index,
                number=index + 1,
                title=f"synced title {index}",
                previous_title=f"previous title {index}",
                title_change_sync_id=sync_id,
                state="open",
                labels=[],
                created_at=now,
                updated_at=now,
            )
            session.add_all([tenant, repo, issue])
            token = create_session_token(
                SessionData(
                    github_id=30_000 + index,
                    login=f"owner-{index}",
                    tenant_slug=slug,
                    role="owner",
                )
            )
            cases.append(
                UndoCase(
                    slug=slug,
                    repo_id=repo.id,
                    issue_id=issue.id,
                    sync_id=sync_id,
                    owner_cookie=token,
                )
            )
        session.commit()
    return cases


async def _request(
    client: httpx.AsyncClient, case: UndoCase, timeout_seconds: float
) -> dict[str, Any]:
    url = (
        f"/api/v1/tenants/{case.slug}/repos/{case.repo_id}/issues/"
        f"{case.issue_id}/title/undo"
    )
    started = time.perf_counter()
    try:
        response = await asyncio.wait_for(
            client.post(
                url,
                params={"sync_id": str(case.sync_id)},
                cookies={"gpc_session": case.owner_cookie},
            ),
            timeout=timeout_seconds,
        )
        return {
            "elapsed_ms": (time.perf_counter() - started) * 1000,
            "http_status": response.status_code,
            "undo_status": response.json().get("status"),
            "error": response.status_code != 200,
            "timeout": False,
        }
    except TimeoutError:
        return {
            "elapsed_ms": (time.perf_counter() - started) * 1000,
            "http_status": None,
            "undo_status": None,
            "error": True,
            "timeout": True,
        }
    except Exception as exc:  # noqa: BLE001 - report harness errors by type only
        return {
            "elapsed_ms": (time.perf_counter() - started) * 1000,
            "http_status": None,
            "undo_status": type(exc).__name__,
            "error": True,
            "timeout": False,
        }


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(percentile * len(ordered) + 0.999999) - 1))
    return round(ordered[index], 3)


async def _run(cases: list[UndoCase], timeout_seconds: float) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    def session_override() -> Generator[Session, None, None]:
        with Session(_engine) as session:
            yield session

    app.dependency_overrides[get_session] = session_override
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            warmup = await _request(client, cases[0], timeout_seconds)
            measured_cases = cases[1:]
            batch_started = time.perf_counter()
            samples = await asyncio.gather(
                *(_request(client, case, timeout_seconds) for case in measured_cases)
            )
            batch_seconds = time.perf_counter() - batch_started
    finally:
        app.dependency_overrides.clear()

    latencies = [sample["elapsed_ms"] for sample in samples]
    report = {
        "environment": {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "database": "SQLite file, synthetic, local process",
            "network": "in-process ASGI; no external calls",
        },
        "dataset": {
            "synthetic_tenants": len(cases),
            "measured_issues_and_handles": len(measured_cases),
            "distinct_tenants_repositories_issues_and_sync_ids": True,
        },
        "request_mix": "POST one undo per distinct existing Issue handle",
        "warmup": {"requests": 1, "http_status": warmup["http_status"]},
        "measurement": {
            "concurrent_tasks": len(measured_cases),
            "samples": len(samples),
            "batch_duration_seconds": round(batch_seconds, 3),
            "timeout_per_request_seconds": timeout_seconds,
            "p50_ms": _percentile(latencies, 0.50),
            "p95_ms": _percentile(latencies, 0.95),
            "p99_ms": _percentile(latencies, 0.99),
            "http_statuses": dict(Counter(str(sample["http_status"]) for sample in samples)),
            "errors": sum(sample["error"] for sample in samples),
            "timeouts": sum(sample["timeout"] for sample in samples),
        },
        "undo_statuses": dict(Counter(str(sample["undo_status"]) for sample in samples)),
        "restored_issues": None,
        "sample_latencies_ms": [round(value, 3) for value in latencies],
    }
    with Session(_engine) as session:
        issue_ids = [case.issue_id for case in measured_cases]
        restored = session.exec(select(Issue).where(Issue.id.in_(issue_ids))).all()
        report["restored_issues"] = sum(
            issue.title == issue.previous_title or issue.previous_title is None
            for issue in restored
        )
        report["all_titles_restored"] = all(
            issue.previous_title is None and issue.title.startswith("previous title ")
            for issue in restored
        )
    return report, samples


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--users", type=int, default=40, help="concurrent undo tasks")
    parser.add_argument("--warmups", type=int, default=1, help="warmup undo requests")
    parser.add_argument("--timeout", type=float, default=10.0, help="per-request timeout")
    parser.add_argument("--output", type=Path, help="also write the JSON report to this path")
    args = parser.parse_args()
    if args.users < 1 or args.warmups != 1:
        parser.error("this harness requires --users >= 1 and exactly one warmup")

    with tempfile.TemporaryDirectory(prefix="vt025-issue-undo-") as temp_dir:
        database_path = Path(temp_dir) / "undo.sqlite3"
        engine = create_engine(
            f"sqlite:///{database_path.as_posix()}",
            connect_args={"check_same_thread": False, "timeout": args.timeout},
            pool_size=args.users + 2,
            max_overflow=0,
        )

        @event.listens_for(engine, "connect")
        def set_busy_timeout(connection: Any, _: Any) -> None:
            connection.execute(f"PRAGMA busy_timeout={int(args.timeout * 1000)}")

        with engine.connect() as connection:
            connection.exec_driver_sql("PRAGMA journal_mode=WAL")
        SQLModel.metadata.create_all(engine)
        global _engine
        _engine = engine
        try:
            cases = _seed(engine, args.users + args.warmups)
            report, _ = asyncio.run(_run(cases, args.timeout))
            output = json.dumps(report, indent=2, sort_keys=True)
            print(output)
            if args.output is not None:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(output + "\n", encoding="utf-8")
        finally:
            engine.dispose()


if __name__ == "__main__":
    main()
