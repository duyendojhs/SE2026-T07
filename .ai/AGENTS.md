# SE2026-T07 Engineering Guidelines for AI Agents

## 1. Technology Stack & Environment Constraints
- **Backend**: Python 3.12, FastAPI, Pydantic v2, SQLModel, PostgreSQL 16.
- **Frontend**: Next.js 14+ (App Router), TypeScript, Tailwind CSS, Lucide Icons.
- **Code Hygiene**: Ruff (Formatting & Linting for Python), ESLint & Prettier (Frontend).
- **Runtime Environment**: Docker Compose (`compose.yml`).

## 2. Non-Negotiable Directives
1. **Zero-Code Retention Policy**:
   - Strictly prohibit fetching, persisting, or analyzing raw source code from student repositories.
   - Process metadata only: commit SHAs, timestamps, commit subjects, issue/PR states, and review events. Never store comment bodies, commit bodies, diffs, patches, or file contents.
   - Findings must be team- or module-level; never create an individual-level "silent member" or performance score.
2. **Rate-Limit Resilience**:
   - All GitHub API integration modules must inspect `X-RateLimit-Remaining` and `X-RateLimit-Reset` headers.
   - Implement exponential backoff, retry mechanisms, and local caching.
3. **Deterministic & Offline Verification**:
   - All automated test suites must execute offline using pre-configured mock fixtures in `backend/tests/mocks/`.
   - Never initiate external HTTP calls during CI/test runs.
4. **Explainable Findings**:
   - The Rule Engine must return structured findings containing explicit reasoning (`rule_id`, `trigger_reason`, `metrics`).
   - Do not generate arbitrary scores or biased personal assessments.
5. **Production Quality**:
   - Refrain from placeholder implementations (e.g., `// TODO: implement later`).
   - Require comprehensive type annotations and corresponding unit tests for every new module.