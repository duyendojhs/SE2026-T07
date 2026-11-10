# ADR-004 — Rule DSL YAML thay vì hard-code

- **Trạng thái:** Accepted
- **Ngày:** 2026-10-21
- **Người quyết định:** SE2026-T07 — Entropy

## Bối cảnh

Các rule như stale PR, review concentration, WIP exceeded cần thay đổi ngưỡng và giải thích được. Hard-code trong Python làm khó test, khó version và dễ tạo logic không minh bạch.

## Quyết định

- Rule được định nghĩa bằng YAML có version.
- Mỗi rule có:
  - `id`, `version`, `title`, `severity`, `scope`;
  - `when` (all/any/not);
  - `evidence` (field path bắt buộc);
  - `action`, `confidence`, `suppression`.
- Rule engine nhận facts deterministic, không truy cập DB trực tiếp.
- `priority_score` được tính deterministic, không do LLM.
- Không rule nào tạo finding cấp cá nhân.

## Hệ quả

- Rule có thể test offline bằng fixture.
- Thay đổi ngưỡng cần tăng version và cập nhật test.
- Cần schema validation cho YAML và registry.
- Finding luôn có evidence để giải thích.
