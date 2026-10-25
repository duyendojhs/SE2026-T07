# ADR-008 — Audit append-only theo hash chain

- **Trạng thái:** Accepted
- **Ngày:** 2026-10-25
- **Người quyết định:** SE2026-T07 — Entropy

## Bối cảnh

Audit phải chứng minh được chuỗi hành động của từng workspace, không lưu login/email và không cho phép sửa hoặc xoá entry giữa chuỗi. Đồng thời hệ thống cần kiểm tra được chuỗi sau khi có checkpoint/archive.

## Quyết định

- Mỗi tenant có một chuỗi riêng; entry đầu dùng `prev_hash = GENESIS` (`0` × 64).
- `entry_hash = SHA256(prev_hash || timestamp || tenant_id || actor_hash || action || resource || request_hash)`.
- Chỉ lưu `actor_hash = HMAC(secret, actor_id)`, không lưu login/email.
- `request_hash` là SHA-256 của payload canonical; không lưu payload thô.
- `audit_logs` không có `deleted_at` và bị chặn update/delete ở tầng ORM.
- Tạo `audit_checkpoints` sau entry đầu tiên và mỗi 1.000 entry. Verify kiểm tra checkpoint rồi đối chiếu toàn chuỗi hiện có.
- Nếu checkpoint bị mất hoặc trỏ tới entry không còn tồn tại, kết quả là `valid: false` hoặc `unknown`, không tự động báo `true`.

## Hệ quả

- Có thể phát hiện sửa/xoá entry và phát hiện checkpoint hỏng.
- Tăng chi phí ghi do phải đọc entry cuối và tạo checkpoint định kỳ.
- Archive về sau phải giữ checkpoint và không được xoá entry giữa chuỗi; đây là tiền đề cho ADR-012 ở S5.
