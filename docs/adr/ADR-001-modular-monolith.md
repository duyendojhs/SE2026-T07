# ADR-001 — Modular monolith thay vì microservices

- **Trạng thái:** Accepted
- **Ngày:** 2026-10-21
- **Người quyết định:** SE2026-T07 — Entropy

## Bối cảnh

Nhóm có 4 thành viên, thời gian triển khai khoảng 9–10 tuần, cần một sản phẩm chạy được với GitHub App, rule engine, dashboard, audit và benchmark. Microservices sẽ tăng chi phí vận hành, debug và CI mà không mang lại lợi ích rõ ràng ở quy mô này.

## Quyết định

Dùng **modular monolith**:

- FastAPI cho backend.
- PostgreSQL 16 cho dữ liệu.
- Redis + ARQ cho background jobs.
- Next.js 14 cho frontend.
- Các module nội bộ tách theo package: `github/`, `ingestion/`, `metrics/`, `rules/`, `graph/`, `coaching/`, `pulse/`, `simulation/`, `ai/`, `audit/`, `exports/`.

Không dùng microservices, message bus riêng, hoặc service mesh.

## Hệ quả

- Deploy đơn giản bằng Docker Compose.
- Dễ test offline và chạy trên máy cá nhân.
- Boundary giữa module phải được giữ bằng quy ước package và code review; không có network boundary.
- Khi cần scale, có thể tách worker hoặc module nặng sau, nhưng không làm trước.
