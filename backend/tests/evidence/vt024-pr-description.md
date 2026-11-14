# PR draft: safe bounded retries for transient GitHub GET failures

## Tóm tắt

- Thêm retry có giới hạn cho GET khi gặp `httpx.ConnectError` hoặc `httpx.TimeoutException`, dùng chính sách backoff hiện hữu.
- Giữ xử lý hiện tại cho GET 403/429/5xx; không retry request unsafe; không retry 401/404.
- Giữ lỗi transport khi cạn lượt; lỗi persistence không thể trả thành công giả.
- Giới hạn production patch ở `backend/app/github/client.py`; không retry toàn bộ backfill.

## Kiểm chứng

- RED: test-only commit `11055810f10729963a8706b22fec2fcf5d9b0647` có bốn test thất bại: timeout, connection error, POST 500 bị retry và retry-bound property. Persistence characterization đã pass trên baseline.
- GREEN: minimal patch `ecd22676f6a1ce43bcfa0d21852f717d475c130d`; 14/14 test retry/backfill pass. Full backend: 48/48 ở Checkpoint 4, sau API persistence regression đạt 49/49 (1 warning deprecation).
- Backend: `49 passed, 1 warning` (`StarletteDeprecationWarning` liên quan Starlette TestClient/httpx).
- Ruff trên retry client, test retry/backfill/API, performance harness và report generator: `All checks passed!`.
- Hypothesis: retry property 40 pass, 2 invalid, 0 fail; idempotency property 30 pass, 4 invalid, 0 fail. Hypothesis không cung cấp dữ liệu cụ thể gây invalid examples.
- Mutation persistence: mutant trả kết quả `ready` giả bị regression test giết bằng `DID NOT RAISE SQLAlchemyError`; mutant đã gỡ khỏi source branch.
- Coverage giới hạn ở GitHubClient và BackfillService: statement 86.62%, branch 73.33%, combined 83.42%.
- Performance chỉ là mock harness: 100 worker, 95 success, 5 exhausted có chủ ý, 115 requests, p95 0.701 ms. Không đại diện hiệu năng production.

## Lệnh tái hiện

Chạy từ thư mục `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --hypothesis-show-statistics tests/test_rate_limit.py tests/test_backfill.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\ruff.exe check app/github/client.py tests/test_rate_limit.py tests/test_backfill.py tests/test_tenants_sync_api.py tests/perf_retry_harness.py tests/evidence/generate_vt024_report.py
.\.venv\Scripts\python.exe -m coverage run --branch --source=app.github.client,app.ingestion.backfill -m pytest -q tests/test_rate_limit.py tests/test_backfill.py tests/test_tenants_sync_api.py
.\.venv\Scripts\python.exe -m coverage report -m
.\.venv\Scripts\python.exe tests/perf_retry_harness.py
```

## Khai báo AI

AI được dùng để hỗ trợ phân tích yêu cầu, đề xuất test, diễn giải log và soạn báo cáo. Các giả định được đối chiếu với mã nguồn/kết quả thực thi; test oracle đã được chỉnh theo contract transport hiện hữu; người nộp chịu trách nhiệm về code, test, kết quả và nội dung cuối. Chi tiết có trong `backend/tests/evidence/vt024-ai-usage-log.md`.

## Giới hạn còn lại

- Mypy không được chạy tại lần xác minh cuối vì module chưa có trong môi trường `.venv` (`No module named mypy`).
- Chưa có test riêng cho 404/generic 4xx, POST transport failure, raw event/audit append count hoặc all-resources-failed.
- Hypothesis invalid-example causes chưa được xác định; coverage không bao phủ toàn repository.
- Performance test không dùng mạng GitHub hoặc database và loại trừ thời gian backoff thật.
- PR được tạo ở trạng thái Draft để review; chưa merge.
