# Privacy & Data Governance Statement

## 1. Zero-Code Retention Policy
GitHub Project Coach (**SE2026-T07**) enforces a strict Zero-Code Retention Policy. The platform never clones, downloads, analyzes, or stores private or public source code files from student repositories.

## 2. Scope of Metadata Ingestion
The system exclusively reads administrative and collaboration metadata via authorized GitHub REST and GraphQL APIs:
- **Commits**: Commit SHA, author username, timestamp, and **commit subject only** (first line; body/footer are never stored).
- **Issues & Pull Requests**: Titles, state transitions (open/closed/merged), labels, assignees, requested reviewers, and lifecycle timestamps.
- **Review Activities**: Review submission timestamps, review state, and review turnaround latency. Comment body is **not** read or stored; only `body_length` and `has_code_block` if needed.
- **Pulse survey (optional)**: Three **pseudonymous** 1–5 items per week (pseudonymous to the server, anonymous to teammates); only team-level aggregate when at least 3 members respond. The server never exposes `respondent_key`.

## 3. Explainability and Impartiality
The platform acts as an objective collaboration coach:
- All risk alerts are **team- or module-level**. The platform does not create findings that name an individual as the problem.
- The platform strictly avoids automated grading, ranking, or qualitative judgment regarding individual student competencies.

## 4. Audit Logging & Security
Every GitHub API interaction and analytical computation is recorded in an append-only audit log table (`audit_logs`), capturing requester ID, target repository, access timestamp, and quota cost. Entries are linked by a per-tenant SHA-256 hash chain with periodic checkpoints; they are archived, not deleted mid-chain.

## 5. Retention & Deletion
- Raw events: 30 days, then aggregate only.
- Commit/comment metadata: 1 year; commit body and comment body are never stored.
- Audit entries: 1 year, then archived with checkpoints; not deleted mid-chain.
- Pulse responses: 90 days; only team-level aggregate is retained.
- Personal data deletion request: completed within 24 hours; audit keeps only an HMAC actor hash.