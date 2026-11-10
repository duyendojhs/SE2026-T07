# ADR-005 — LLM chỉ narrates, không computes

- **Trạng thái:** Accepted
- **Ngày:** 2026-10-21
- **Người quyết định:** SE2026-T07 — Entropy

## Bối cảnh

LLM có thể viết summary dễ đọc nhưng không đáng tin để tự tính metric hoặc tự chọn finding. Sản phẩm cần số liệu kiểm chứng được và không được tạo cảm giác “AI bịa số”.

## Quyết định

- Metric, rule, priority và evidence do code deterministic tạo ra.
- LLM chỉ nhận facts đã lọc và viết narrative.
- Mọi câu summary có citation tới field/finding.
- Validator kiểm tra số trong output khớp facts; nếu không, fallback template không dùng LLM.
- Nếu thiếu dữ liệu, LLM phải refusal theo mẫu, không suy đoán.
- Q&A trên facts là stretch S5, có endpoint/tool allowlist và eval riêng; không tính vào MVP.

## Hệ quả

- Chất lượng summary phụ thuộc chất lượng facts.
- Cần LLM eval tối thiểu 20 case, gồm grounded, refusal, prompt injection và số bịa.
- Có thể tắt LLM và vẫn có dashboard/summary dạng bullet.
- Không dùng LLM để chấm điểm, xếp hạng hoặc đánh giá cá nhân.
