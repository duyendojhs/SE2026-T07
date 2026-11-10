# ADR-006 — PostgreSQL thay vì graph database

- **Trạng thái:** Accepted
- **Ngày:** 2026-10-25
- **Người quyết định:** SE2026-T07 — Entropy

## Bối cảnh

Sản phẩm cần lưu metadata GitHub, findings, audit hash chain, agreement, intervention và pulse. Phần lớn truy vấn là lọc theo `tenant_id`, repo, khoảng thời gian và trạng thái; graph chỉ là một cách trình bày ở S3, không phải nguồn dữ liệu chính. Nhóm nhỏ, cần giảm chi phí vận hành và giữ transaction rõ ràng cho audit.

## Quyết định

Dùng **PostgreSQL 16** làm datastore duy nhất cho MVP:

- Mọi bảng nghiệp vụ có `tenant_id`; index tổ hợp bắt đầu bằng `tenant_id` khi truy vấn theo tenant.
- Dùng UUID cho khoá chính, `timestamptz` cho thời gian, JSONB cho payload đã lọc.
- Quan hệ thành viên/review/comment/commit lưu bằng foreign key; graph view dựng bằng query/aggregation ở tầng ứng dụng.
- Không thêm Neo4j hay graph database riêng trong MVP.

## Hệ quả

- Một database, một migration chain, backup và kiểm soát quyền đơn giản.
- Graph query phức tạp hơn có thể chậm; khi cần, thêm materialized view hoặc bảng aggregate trước khi cân nhắc graph DB.
- Nếu sau này tách graph store, PostgreSQL vẫn là source of truth và contract `tenant_id` không đổi.
