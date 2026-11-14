# VT-024 Test Traceability

The repository tests do not define separate `T01`/`TC-01` case identifiers. To avoid inventing IDs, the Test Case ID column is marked **not assigned**; the exact test function is the executable identity. Commit hashes show where the test/evidence was introduced or materially corrected.

| Acceptance criterion / risk | Test Case ID | Test function / experiment | Test file | Commit SHA | Actual result |
|---|---|---|---|---|---|
| AC-01: transient HTTP 5xx retry | Not assigned | `test_http_500_is_retried_then_succeeds` | `backend/tests/test_rate_limit.py` | `11055810f10729963a8706b22fec2fcf5d9b0647` | Pass; first 500 then 200. |
| AC-01: timeout retry | Not assigned | `test_read_timeout_is_retried_then_succeeds` | `backend/tests/test_rate_limit.py` | `11055810f10729963a8706b22fec2fcf5d9b0647` | Pass; first ReadTimeout then 200. |
| AC-01: connection error retry | Not assigned | `test_connection_error_is_retried_then_succeeds` | `backend/tests/test_rate_limit.py` | `11055810f10729963a8706b22fec2fcf5d9b0647` | Pass; first ConnectError then 200. |
| AC-02: bounded attempts, success only after success, exhausted transport error propagation | Not assigned | `test_timeout_retry_is_bounded_and_returns_only_after_success` | `backend/tests/test_rate_limit.py` | Test added in `11055810f10729963a8706b22fec2fcf5d9b0647`; oracle corrected in `ecd22676f6a1ce43bcfa0d21852f717d475c130d` | Pass; 40 passing Hypothesis examples, 2 invalid generated examples, 0 failures. It asserts at most `max_retries + 1` calls and propagates `httpx.TransportError` on exhaustion. |
| AC-02: non-retryable auth error | Not assigned | `test_bad_token_is_not_retried` | `backend/tests/test_rate_limit.py` | `11055810f10729963a8706b22fec2fcf5d9b0647` | Pass; one attempt, 401 error propagated. |
| AC-02: unsafe request not retried on transient HTTP status | Not assigned | `test_transient_http_error_on_post_is_not_retried` | `backend/tests/test_rate_limit.py` | `11055810f10729963a8706b22fec2fcf5d9b0647` | Pass; POST receives 500 once and raises. |
| AC-02: retry exhaustion does not return success | Not assigned | `test_rate_limit_exhaustion_raises` | `backend/tests/test_rate_limit.py` | `11055810f10729963a8706b22fec2fcf5d9b0647` | Pass; repeated 403 ends in `GitHubAPIError`. |
| AC-03: duplicate/reordered ingestion retains unique business records | Not assigned | `test_generated_duplicate_issue_ids_remain_unique_after_reordered_reingestion` | `backend/tests/test_backfill.py` | `11055810f10729963a8706b22fec2fcf5d9b0647` | Pass; 30 passing Hypothesis examples, 4 invalid generated examples, 0 failures. |
| AC-03: repeated backfill is idempotent for business rows | Not assigned | `test_backfill_is_idempotent_and_metadata_only` | `backend/tests/test_backfill.py` | `7c13113429ffb279c0128bf8030d5804ad35933e` | Pass; business-row counts remain stable. RawEvent/audit counts after the second run are not asserted. |
| AC-04: service persistence failure never returns successful result; recovery works | Not assigned | `test_commit_failure_never_returns_success_and_recovery_is_consistent` | `backend/tests/test_backfill.py` | Test introduced in `11055810f10729963a8706b22fec2fcf5d9b0647`; event alias/cleanup review in `ecd22676f6a1ce43bcfa0d21852f717d475c130d` | Pass on correct implementation; raises the injected SQLAlchemyError, verifies no issue/PR rows after rollback, then recovers. It killed the deliberate false-success mutant. |
| AC-04: API persistence error not reported as success | Not assigned | `test_sync_api_does_not_return_success_when_persistence_fails` | `backend/tests/test_tenants_sync_api.py` | `e4e56c86b9dab3e3e3c2fbaf36b751f29e4b135a` | Pass; authenticated request with offline fake client returns HTTP 500 and repo remains pending. |
| AC-04: deliberate false-success mutation | Not assigned (mutation experiment) | Mutated `BackfillService.run()` commit block, then ran `test_commit_failure_never_returns_success_and_recovery_is_consistent` | `backend/tests/test_backfill.py`; output/diff in `backend/tests/evidence/vt024-mutation.txt` and `vt024-mutation-diff.patch` | Test in `11055810f10729963a8706b22fec2fcf5d9b0647`; mutation evidence in `e4e56c86b9dab3e3e3c2fbaf36b751f29e4b135a` | Mutant killed: test failed with `DID NOT RAISE SQLAlchemyError`, as expected. Mutant absent from submission branch. |
| AC-05: partial ingestion status/data behavior | Not assigned | `test_backfill_marks_partial_when_one_resource_fails` | `backend/tests/test_backfill.py` | `7c13113429ffb279c0128bf8030d5804ad35933e` | Pass; review endpoint failure produces `partial`, records an error, and successful issue/PR data remain. |
| Performance: 100 concurrent mocked tasks and p95 sample | Not assigned (standalone harness) | `main` / `_run_task` | `backend/tests/perf_retry_harness.py` | Initial harness in `e4e56c86b9dab3e3e3c2fbaf36b751f29e4b135a`; 100-worker barrier and corrected reporting in `5f1fcbb719a8efad847e58bca03dce406566bfae` | Pass: all 100 workers rendezvous before timing; 95 succeeded, 5 intentionally exhausted; 115 requests; 5% error rate; latest mock sample p50 0.376 ms, p95 0.701 ms, max 1.131 ms. Not production/API/database performance. |

## Commit chain

- Baseline: `90f831c8c8afc84dd4f0268b7ed5704e41f32cbf`
- Existing backfill tests: `7c13113429ffb279c0128bf8030d5804ad35933e`
- RED test commit: `11055810f10729963a8706b22fec2fcf5d9b0647`
- GREEN production retry and oracle correction: `ecd22676f6a1ce43bcfa0d21852f717d475c130d`
- Phase 4 API/coverage/performance evidence commit: `e4e56c86b9dab3e3e3c2fbaf36b751f29e4b135a`
- Checkpoint 6 performance refinement and corrected experiment: `5f1fcbb719a8efad847e58bca03dce406566bfae`
