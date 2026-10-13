# Privacy & Data Governance Statement

## 1. Zero-Code Retention Policy
GitHub Project Coach (**SE2026-T07**) enforces a strict Zero-Code Retention Policy. The platform never clones, downloads, analyzes, or stores private or public source code files from student repositories.

## 2. Scope of Metadata Ingestion
The system exclusively reads administrative and collaboration metadata via authorized GitHub REST and GraphQL APIs:
- **Commits**: Commit SHA, author username, timestamp, and commit messages.
- **Issues & Pull Requests**: Titles, state transitions (open/closed/merged), labels, assignees, requested reviewers, and lifecycle timestamps.
- **Review Activities**: Review submission timestamps, review comments volume, and review turnaround latency.

## 3. Explainability and Impartiality
The platform acts as an objective collaboration coach:
- All risk alerts (e.g., stale pull requests, review bottlenecks) are evaluated through deterministic, explainable rule sets.
- The platform strictly avoids automated grading, ranking, or qualitative judgment regarding individual student competencies.

## 4. Audit Logging & Security
Every GitHub API interaction and analytical computation is recorded in an immutable audit log table (`audit_logs`), capturing requester ID, target repository, access timestamp, and quota cost.