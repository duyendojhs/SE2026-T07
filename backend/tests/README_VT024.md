# VT-024: bounded retry cho GitHub API

## Vấn đề và phạm vi

VT-024 kiểm tra việc retry các lỗi tạm thời khi đọc GitHub API. Bản sửa trong `app/github/client.py` retry có giới hạn cho GET khi gặp HTTP 403/429/5xx theo chính sách hiện hữu, `httpx.ConnectError` hoặc `httpx.TimeoutException`. Request không an toàn không được retry tự động; lỗi 401/404 không retry; hết lượt phải phát sinh lỗi. Allowlist endpoint, xác thực và backoff hiện có được giữ lại. Không có retry toàn quy trình backfill.

## Yêu cầu

- Python 3.12 trở lên.
- Cài dependency backend và nhóm kiểm thử từ thư mục `backend`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Lệnh cài đặt dùng `coverage` trong nhóm dev để tái tạo báo cáo coverage; mypy là dependency được khai báo nhưng lần kiểm tra này không chạy được vì module chưa có trong môi trường `.venv`.

## Lệnh kiểm thử và đánh giá

Chạy từ `backend` trong PowerShell:

```powershell
# Retry + backfill; hiển thị thống kê Hypothesis
.\.venv\Scripts\python.exe -m pytest -q --hypothesis-show-statistics tests/test_rate_limit.py tests/test_backfill.py

# Toàn bộ backend
.\.venv\Scripts\python.exe -m pytest -q

# Ruff trên mã nguồn và kiểm thử của vertical slice
.\.venv\Scripts\ruff.exe check app/github/client.py tests/test_rate_limit.py tests/test_backfill.py tests/test_tenants_sync_api.py tests/perf_retry_harness.py

# Coverage có branch; chỉ hai production module thuộc phạm vi
.\.venv\Scripts\python.exe -m coverage run --branch --source=app.github.client,app.ingestion.backfill -m pytest -q tests/test_rate_limit.py tests/test_backfill.py tests/test_tenants_sync_api.py
.\.venv\Scripts\python.exe -m coverage report -m
.\.venv\Scripts\python.exe -m coverage json -o tests/evidence/vt024-coverage.json

# Harness hiệu năng mock
.\.venv\Scripts\python.exe tests/perf_retry_harness.py
```

## Bằng chứng

- RED ban đầu: `tests/evidence/vt024-red.txt`, `vt024-red-context.txt`.
- GREEN: `vt024-green.txt`, `vt024-green-context.txt`; hồi quy cuối: `vt024-final-tests.txt`.
- Mutation và xác nhận đã gỡ: `vt024-mutation.txt`, `vt024-mutation-diff.patch`, `vt024-mutation-removal.txt`.
- Coverage và diễn giải: `vt024-coverage-run.txt`, `vt024-coverage-report.txt`, `vt024-coverage.json`, `vt024-coverage-review.md`.
- Flaky/performance: `vt024-flaky-orders.txt`, `vt024-flaky-review.md`, `vt024-performance.txt`.
- Traceability và nhật ký AI: `vt024-traceability.md`, `vt024-ai-usage-log.md`.
- Báo cáo: `output/pdf/BT3_23001819_VT-024.pdf`.

## Kết quả và giới hạn đã biết

Ở lần xác minh cuối: `49 passed, 1 warning`; Ruff báo `All checks passed!`. Cảnh báo còn lại là Starlette deprecation khi `starlette.testclient` dùng `httpx`. Mypy không được xác minh: môi trường trả về `No module named mypy`. Coverage được giới hạn ở hai module đã nêu, không đại diện coverage toàn repository. Hypothesis ghi nhận 2 invalid examples ở property retry và 4 ở property ingest, không có failure; nguyên nhân cụ thể không được Hypothesis xuất ra. Performance harness dùng mock, không có chờ backoff thật, mạng GitHub hay database; p95 này không phải p95 production. Xem các file bằng chứng và báo cáo để biết số liệu, phạm vi và rủi ro chi tiết.
