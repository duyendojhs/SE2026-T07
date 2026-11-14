# VT-024 Flaky-Test Review

## Time, sleep, and backoff

- `test_rate_limit_retry_after_is_respected` uses a fake sleep callback that records the requested delay and asserts the configured `Retry-After` value; it does not wait one second.
- Timeout, connection-error, HTTP 5xx, and bounded property tests use `sleep=lambda _: None`, so no real backoff delay is part of their pass/fail behavior.
- `GitHubClient` adds random jitter to fallback backoff, but the tests do not assert that random value and their sleep callback is a no-op. This avoids wall-clock flakes while leaving production timing/backoff duration unmeasured by those tests.
- The timing test uses monotonic `time.perf_counter` only for reporting; there is no latency threshold assertion in pytest.

## Hypothesis inputs and shrinking

- Retry property: `@settings(max_examples=40, derandomize=True, database=None)`; result was 40 passing, 2 invalid, 0 failing.
- Idempotency property: `@settings(max_examples=30, derandomize=True, database=None)`; result was 30 passing, 4 invalid, 0 failing.
- Neither test has `assume()` or `.filter()`. A temporary no-op probe using the same bounded strategy also produced invalid generated examples (3 in that probe). The production test bodies do not report a minimized failure. Hypothesis's captured statistics do not identify the serialized data for each invalid example, so the exact internal generation cause remains unresolved.

## Test order and shared state

- Ran both `tests/test_rate_limit.py tests/test_backfill.py tests/test_tenants_sync_api.py` and the reversed order `tests/test_backfill.py tests/test_tenants_sync_api.py tests/test_rate_limit.py`; each run passed 15 tests. Exact commands/output are in `vt024-flaky-orders.txt`.
- Pytest database fixtures create an in-memory SQLite engine per test. The property test also creates/drops its own isolated engine.
- The API failure test removes its `get_session` dependency override and SQLAlchemy event listener in `finally`; the full suite passed after the API test was included.

## Concurrency and external services

- Tests use `httpx.MockTransport` or local fake clients; no GitHub API calls are made, so network variability is not part of automated results.
- The performance harness runs 100 executor workers and waits for all 100 at a barrier before measured work. Each task owns its client, mock handler, and attempt counter. One mock run passed with 95 success outcomes and 5 intentionally exhausted outcomes. Mock latency is not a substitute for concurrent API/database or real network testing.
