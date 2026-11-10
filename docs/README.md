# Tài liệu dự án SE2026-T07 (GitHub Project Coach)

Mục lục tài liệu kỹ thuật, kiến trúc và tiến độ của dự án.

## 1. Nền tảng và hợp đồng kỹ thuật

- [BUILD CONTRACT](BUILD-CONTRACT.md): Invariants (I-01 đến I-14), quyết định kiến trúc đã freeze, tiêu chuẩn sprint gate và acceptance checks.
- [AI Agent Directives](../.ai/AGENTS.md): Ràng buộc kỹ thuật bắt buộc cho AI agents khi tham gia lập trình.
- [Privacy Policy](../PRIVACY.md): Chính sách bảo mật metadata-only, zero-code retention và ranh giới quyền riêng tư.

## 2. Quyết định kiến trúc (Architecture Decision Records)

Thư mục: [`adr/`](adr/README.md)

- [ADR-001: Modular Monolith Architecture](adr/ADR-001-modular-monolith.md)
- [ADR-002: Multi-Tenant Architecture](adr/ADR-002-multi-tenant.md)
- [ADR-003: Metadata-Only Privacy Boundary](adr/ADR-003-metadata-only.md)
- [ADR-004: Versioned Rule Engine DSL](adr/ADR-004-rule-dsl.md)
- [ADR-005: LLM Narrates, Never Scores](adr/ADR-005-llm-narrates.md)
- [ADR-006: PostgreSQL Schema & Relational Storage](adr/ADR-006-postgresql.md)
- [ADR-008: Append-Only Cryptographic Audit Hash Chain](adr/ADR-008-audit-hash-chain.md)

## 3. Kiến trúc Frontend

- [Kiến trúc Frontend](frontend/architecture.md): Cấu trúc thư mục Next.js 14 App Router, phân vùng Feature-based & Shared, ranh giới Server/Client Component, quy ước thiết kế và hướng tích hợp API.
- Hướng dẫn vận hành frontend: xem [`frontend/README.md`](../frontend/README.md).

## 4. Nhật ký Task & Tiến độ

- [Task #8 — Khởi tạo và refactor kiến trúc frontend](tasks/08-frontend-refactor.md): Bối cảnh, các quyết định kiến trúc D01–D05, các phần đã tái cấu trúc, kết quả kiểm chứng và lộ trình tiếp theo.
