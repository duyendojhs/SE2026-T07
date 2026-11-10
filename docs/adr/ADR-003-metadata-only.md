# ADR-003 — Metadata-only và field allowlist

- **Trạng thái:** Accepted
- **Ngày:** 2026-10-21
- **Người quyết định:** SE2026-T07 — Entropy

## Bối cảnh

Sản phẩm phân tích quy trình cộng tác, không cần đọc source code. Việc lưu code, diff, patch hoặc nội dung comment/commit body tạo rủi ro privacy và vượt quá phạm vi đồ án.

## Quyết định

- Chỉ đọc metadata qua GitHub API.
- Dùng allowlist trường trước khi ghi DB/log.
- Không đọc/lưu:
  - `patch`, `diff`, `blob`, file content;
  - comment body;
  - commit body/footer.
- `commit.message` chỉ đọc transient để lấy dòng đầu thành `message_subject` (tối đa 200 ký tự).
- Comment chỉ lưu `body_length` và `has_code_block`.
- `strip_payload()` chạy trước khi ghi DB và trước khi log.

## Hệ quả

- Giảm rủi ro privacy và dung lượng lưu trữ.
- Một số phân tích code-level bị loại bỏ có chủ đích.
- Cần test fixture không chứa khóa bị cấm và test redaction log.
- Nếu GitHub API không trả file path tách biệt, bỏ tính năng module-level thay vì lấy patch.
