# Architecture Decision Records

Các quyết định kiến trúc của SE2026-T07. ADR chỉ bị thay thế bằng một ADR mới, không sửa lịch sử.

| ADR | Quyết định | Trạng thái |
|---|---|---|
| [ADR-001](ADR-001-modular-monolith.md) | Modular monolith thay vì microservices | Accepted |
| [ADR-002](ADR-002-multi-tenant.md) | Multi-tenant theo `tenant_id` | Accepted |
| [ADR-003](ADR-003-metadata-only.md) | Metadata-only + field allowlist | Accepted |
| [ADR-004](ADR-004-rule-dsl.md) | Rule DSL YAML thay vì hard-code | Accepted |
| [ADR-005](ADR-005-llm-narrates.md) | LLM chỉ narrates, không computes | Accepted |
| [ADR-006](ADR-006-postgresql.md) | PostgreSQL thay vì graph DB | Accepted |
| [ADR-008](ADR-008-audit-hash-chain.md) | Audit hash chain append-only | Accepted |

Các ADR tiếp theo:

- ADR-007 Simulator DES — trước S4.
- ADR-009 Không individual score — trước S2.
- ADR-010 Level 5 = field study + benchmark — trước S5.
- ADR-011 Pulse pseudonymous — trước S4.
- ADR-012 Audit archive + checkpoint — trước S5.
