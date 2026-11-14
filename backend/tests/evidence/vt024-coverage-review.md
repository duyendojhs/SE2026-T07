# VT-024 Coverage and Risk Review

## Commands and scope

Coverage was collected for only the selected GitHub retry/backfill vertical slice, not the repository:

```powershell
.\.venv\Scripts\python.exe -m coverage run --branch --source=app.github.client,app.ingestion.backfill -m pytest -q tests/test_rate_limit.py tests/test_backfill.py tests/test_tenants_sync_api.py
.\.venv\Scripts\python.exe -m coverage report -m
.\.venv\Scripts\python.exe -m coverage json -o tests/evidence/vt024-coverage.json
```

The selected test run passed 15 tests. Raw terminal outputs are in `vt024-coverage-run.txt` and `vt024-coverage-report.txt`; the machine-readable branch details are in `vt024-coverage.json`.

## Correct interpretation of coverage.py metrics

The text report's `Cover` column includes statements and branch arcs; its 74%, 92%, and 83% values are **combined coverage**, not line-only coverage. The JSON separates statement and branch rates:

| Production module | Covered statements / statements | Statement coverage | Covered branches / branches | Branch coverage | Combined coverage.py `Cover` |
|---|---:|---:|---:|---:|---:|
| `app/github/client.py` | 95 / 121 | 78.51% (79%) | 31 / 50 | 62.00% | 73.68% (74%) |
| `app/ingestion/backfill.py` | 151 / 163 | 92.64% (93%) | 35 / 40 | 87.50% (88%) | 91.63% (92%) |
| Selected-module total | 246 / 284 | 86.62% (87%) | 66 / 90 | 73.33% (73%) | 83.42% (83%) |

`covered_lines` in coverage.py JSON is the count of executed statements; the displayed line/statement rate is computed against executable statements. Twenty branch decision points are partial; they contribute 24 missing branch arcs. This is not full-repository coverage.

## Uncovered paths relevant to risk

- `GitHubClient`: safe GET retries for 5xx, `ConnectError`, and timeout and the bounded exhaustion path are exercised. Missing branch arcs include rate-reset waiting (`client.py:69-75`), absent/malformed `Retry-After` fallback (`123-130`), generic 4xx propagation (`142-146`), 304 handling (`110`, `159`, `181`), and malformed/non-list pagination cases (`184-189`, `200-207`). There is no distinct direct test for 404 or 429, though 401 and 403 cases exercise their shared code branches.
- `BackfillService`: partial failure with some ingested counts is tested. The all-resources-fail path that yields `error` rather than `partial` (`backfill.py:106-108`) is not directly covered. Remaining missing arcs include skipping an issue that is also a PR (`129-130`), stale PR cutoff (`153-154`), and missing PR during review ingestion (`172-173`).
- These gaps are not hidden by the selected-module percentages. The safe retry and persistence invariants have direct targeted tests; unrelated client utility paths remain uncovered by this slice.

## Acceptance-criterion risk coverage

| Criterion | Evidence exercised | Risk coverage conclusion |
|---|---|---|
| AC-01 transient 5xx/connection/timeout retries within a configured bound | `test_http_500_is_retried_then_succeeds`, `test_read_timeout_is_retried_then_succeeds`, `test_connection_error_is_retried_then_succeeds`, and bounded retry property | Strong for selected GET transport/status cases. No live network behavior is claimed. |
| AC-02 immediate propagation for non-retryable errors and failure on exhaustion | `test_bad_token_is_not_retried`, `test_transient_http_error_on_post_is_not_retried`, `test_rate_limit_exhaustion_raises`, bounded retry property | Good for 401, POST/500, 403 exhaustion, and transport exhaustion. 404, generic 4xx, and POST transport-error cases lack distinct direct tests. |
| AC-03 repeated metadata does not duplicate business records/side effects | `test_backfill_is_idempotent_and_metadata_only`, `test_generated_duplicate_issue_ids_remain_unique_after_reordered_reingestion` | Business-row uniqueness is exercised. RawEvent and audit append counts are not asserted; repeated whole backfills can append additional RawEvent/audit records, so exact-once secondary side effects remain unproven and are a known risk. |
| AC-04 persistence failure never yields success | `test_commit_failure_never_returns_success_and_recovery_is_consistent`, `test_sync_api_does_not_return_success_when_persistence_fails`, deliberate false-success mutant | Strong for service result and API response. The mutant was killed by the commit-failure regression. |
| AC-05 partial ingestion preserves consistency/status | `test_backfill_marks_partial_when_one_resource_fails` | Partial status and surviving business rows are directly exercised. All-resources-failed status and cross-resource rollback behavior are not separately covered. |

## Mutation and source-integrity cross-check

At Checkpoint 6, the assignment branch has no working-tree changes; `git diff 90f831c8c8afc84dd4f0268b7ed5704e41f32cbf HEAD -- backend/app/ingestion/backfill.py` is empty. The intentional mutation is preserved only as evidence in `vt024-mutation-diff.patch`; it is not present in the branch source. The RED, GREEN, and quality-evidence commits remain in history.
