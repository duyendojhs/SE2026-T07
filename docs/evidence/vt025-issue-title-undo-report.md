# VT-025 Issue title undo evidence

Date: 2026-11-14 (Asia/Bangkok)
Repository: `https://github.com/duyendojhs/SE2026-T07.git`
Branch: `feat/issue-title-undo-vt025`
Baseline: `00243482997739a097f5609abdeae83043f8fb45`
Code/test commit: `94c94d0` (`feat: add undo for synced issue titles`)
Implementation Guide: `D:\SE\docs\04-implementation\SE2026_T07-Implementation-Guide.md` was absent. Work followed `.ai/AGENTS.md`, `docs/BUILD-CONTRACT.md`, and the present ADRs; no concrete contradiction was found.

## Test evidence

The commands ran offline with `DATABASE_URL=sqlite://` and the project’s declared development dependencies. SQLite was used for the backend test fixtures; no service outside the process was called.

| Stage | Command | Result |
|---|---|---|
| Baseline before implementation | `rtk proxy "C:\Users\ANHTRU~1\AppData\Local\Temp\se2026-t07-vt025-venv\Scripts\python.exe" -c "import os,sys; os.environ['DATABASE_URL']='sqlite://'; import pytest; sys.exit(pytest.main())"` | `41 passed, 1 warning in 0.96s` |
| Test-first red before implementation | Same runner with `pytest.main(['tests/test_normalizer.py','tests/test_backfill.py','tests/test_issue_title_undo.py','--tb=short'])` | `16 failed, 11 passed, 1 warning`; failures exposed invalid title normalization/upsert behavior and the missing undo handle in sync response |
| Focused final suite | Same runner with `pytest.main(['tests/test_normalizer.py','tests/test_backfill.py','tests/test_issue_title_undo.py','--tb=short'])` | `32 passed, 1 warning in 0.91s` |
| Full final backend suite | Same runner with `pytest.main(['--tb=short'])` | `67 passed, 1 warning in 1.67s` |
| Ruff | `rtk proxy "C:\Users\ANHTRU~1\AppData\Local\Temp\se2026-t07-vt025-venv\Scripts\ruff.exe" check .` | `All checks passed!` |
| Mypy | `rtk proxy "C:\Users\ANHTRU~1\AppData\Local\Temp\se2026-t07-vt025-venv\Scripts\python.exe" -m mypy app` | `Success: no issues found in 27 source files` |
| Diff whitespace | `rtk proxy git diff --check` | exit 0 |

The single test warning is Starlette’s deprecation warning for using `httpx` with `starlette.testclient`; it did not fail the suite. The baseline used the original 41 tests. The final suite includes the new normalizer, backfill, and API tests.

Line/branch coverage was not measured: neither `coverage` nor `pytest-cov` is installed in the existing environment. No dependency was added for this assignment.

## Authorization mutation

The mutation was performed only in a temporary worktree based on commit `94c94d0`. I removed the `require_role` guard from the Issue title undo route and ran:

```text
pytest tests/test_issue_title_undo.py::test_authenticated_viewer_cannot_undo --tb=short
```

Expected mutation result: **1 failed** because the viewer received HTTP `200` while the test expected `403`. After restoring the guard, the same command reported **1 passed**. The temporary worktree then had an empty `git status` and no diff; the temporary checkout was removed. The mutation was not committed.

## Migration and PostgreSQL availability

The migration was exercised on SQLite using `upgrade head → downgrade to 3ffc12e866fb → upgrade head`; both nullable undo columns appeared after each upgrade and disappeared after downgrade. Result: `SQLite migration upgrade -> downgrade -> upgrade passed`.

PostgreSQL race/migration verification was unavailable locally: `localhost:5432` was unavailable, and `docker version --format '{{.Server.Version}}'` could not connect to the Docker engine named pipe. SQLite verified the conditional update and sequential stale/retry behavior in tests, but does not prove PostgreSQL transaction races.

## 40-task performance harness

Command, run twice from `backend/`:

```text
python scripts/benchmark_issue_title_undo.py --users 40 --warmups 1 --output ../docs/evidence/vt025-issue-title-load-run-1.json
python scripts/benchmark_issue_title_undo.py --users 40 --warmups 1 --output ../docs/evidence/vt025-issue-title-load-run-2.json
```

The script sends 1 warmup request, then 40 concurrent `POST` requests. Each measured request has a distinct synthetic tenant, repository, Issue, owner session, and undo token. It exercises the FastAPI route through an in-process ASGI transport, backed by a temporary SQLite file, and calls no external service. Per-request timeout was 10 seconds; there were 40 latency samples per run.

| Run | Batch duration | p50 | p95 | p99 | HTTP 200 | Errors | Timeouts | Restored |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1.748 s | 523.762 ms | 1616.237 ms | 1727.014 ms | 40/40 | 0 | 0 | 40/40 |
| 2 | 2.081 s | 420.065 ms | 1855.557 ms | 2061.900 ms | 40/40 | 0 | 0 | 40/40 |

Both measured p95 values exceed 1.5 seconds in this SQLite harness. This is not a production performance result: SQLite serializes writes, the ASGI transport runs in-process, and this batch does not include the sync/GitHub network path. No claim that the VT-025 production p95 target is met is supported by these runs. Full per-request latencies and request counts are in [`run 1 JSON`](vt025-issue-title-load-run-1.json) and [`run 2 JSON`](vt025-issue-title-load-run-2.json).

## Flaky-test risks and controls

- Backfill fixture timestamps previously sat at fixed dates near the 90-day filter. They now derive from the current UTC time and stay within three days of the run, so the PR fixture does not age out of the tested window.
- The audit test previously treated the last row of an unordered query as the undo entry. It now selects by the `issue.title.undo` action and asserts the resource, so query order does not decide the result.
- The 40-task SQLite timing is sensitive to writer-lock scheduling. Two runs are retained separately; these measurements are harness evidence only. Pytest database fixtures remain isolated per test, and all test GitHub clients are fakes.

## Scope and remaining evidence limits

The final code commit changes only Issue title handling/undo. `normalize_pull_request` behavior remains covered by its 501-character truncation regression. Titles are not included in the undo response, audit payload, or Issue RawEvent. The tests prove local snapshot restoration; GitHub was not changed. No PostgreSQL service was available for a same-Issue concurrent race test, and the performance target still needs a representative PostgreSQL/API environment measurement.
