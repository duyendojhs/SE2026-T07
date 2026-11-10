# ADR-002 — Multi-tenant theo `tenant_id`

- **Trạng thái:** Accepted
- **Ngày:** 2026-10-21
- **Người quyết định:** SE2026-T07 — Entropy

## Bối cảnh

Sản phẩm chỉ phục vụ **một nhóm mỗi workspace**, nhưng vẫn cần cách ly dữ liệu giữa các nhóm nếu triển khai cho nhiều nhóm hoặc dùng chung hạ tầng. Không có dashboard cho giảng viên, không so sánh chéo nhóm.

## Quyết định

- Mọi bảng nghiệp vụ có `tenant_id`.
- Mọi query đọc/ghi đều lọc theo `tenant_id`.
- `tenants` là bảng gốc; workspace được resolve từ slug.
- Không có API trả dữ liệu tổng hợp cross-tenant.
- Có thể bật PostgreSQL Row-Level Security sau, nhưng application-level filtering là bắt buộc ngay từ S1.

## Hệ quả

- Tránh rò rỉ dữ liệu giữa các nhóm.
- Tăng độ phức tạp nhẹ ở mọi query và test.
- Phải có test cố định: query thiếu `tenant_id` phải fail.
- Không hỗ trợ dashboard so sánh nhóm, kể cả khi có nhiều tenant.
