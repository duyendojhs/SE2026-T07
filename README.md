# GitHub Project Coach (SE2026-T07)

An AI-augmented engineering analytics platform designed to detect student collaboration bottlenecks, monitor project velocity, and generate weekly progress summaries using explainable rules and metadata telemetry.

## Team Entropy

- **Do Minh Duyen** (Lead) — System Architecture & GitHub Data Ingestion
- **Ban Khanh Duy** — Analytics, Explainable Rule Engine & LLM Pipeline
- **Truong The Anh** — Frontend Engineering & Data Visualization
- **Hoang Khanh An** — QA Engineering, Security Compliance & DevOps

## Repository Structure

- `backend/` — FastAPI services, rate-limited GitHub client, rule engine, and audit logs.
- `frontend/` — Next.js 14 dashboard app (feature-based architecture); full dashboard live data starts in S3.
- `docs/` — build contract, architecture decisions, task records, and technical specifications.
- `.ai/` — AI agent directives (`AGENTS.md`).

## Quick Start

### Backend + database (Docker Compose)

```bash
docker compose up -d --build
```

Backend health:

```text
http://localhost:8000/health
```

Stop:

```bash
docker compose down
```

### Backend local

```bash
cd backend
python -m pip install -e ".[dev]"
alembic upgrade head
ruff check .
mypy app
pytest
```

Copy `.env.example` to `.env` and fill GitHub App/OAuth values when they are
available. In development without credentials, `/health`, `/ready`, schema,
unit tests and fixture backfill still run; live App installation and sync return
`503` instead of falling back to a PAT.

### Issue title undo tests and local harness

From PowerShell, run the focused offline tests, the full backend suite, and the
40-task synthetic harness from `backend/`:

```powershell
cd backend
$env:DATABASE_URL = "sqlite://"
python -m pytest tests/test_normalizer.py tests/test_backfill.py tests/test_issue_title_undo.py
python -m pytest
python scripts/benchmark_issue_title_undo.py --users 40 --warmups 1 --output ../docs/evidence/vt025-issue-title-load-run-1.json
python scripts/benchmark_issue_title_undo.py --users 40 --warmups 1 --output ../docs/evidence/vt025-issue-title-load-run-2.json
```

The harness uses synthetic SQLite data and an in-process ASGI transport. Its
latencies do not represent PostgreSQL or production network performance; see
[`docs/evidence/vt025-issue-title-undo-report.md`](docs/evidence/vt025-issue-title-undo-report.md).

### Frontend local

```bash
cd frontend
npm ci
npm run dev
```

## Current Sprint

**S1** — GitHub OAuth/App auth, tenant-scoped schema and migration, 90-day
metadata backfill, webhook intake, append-only audit hash chain, and offline
tests. ADR-006 and ADR-008 are accepted.

S1 endpoints:

```text
GET  /health
GET  /ready
GET  /api/v1/auth/github/login
GET  /api/v1/auth/github/install
GET  /api/v1/auth/github/install/callback
GET  /api/v1/me
GET  /api/v1/tenants/{slug}/repos
POST /api/v1/tenants/{slug}/repos/{repo_id}/sync
POST /api/v1/tenants/{slug}/repos/{repo_id}/issues/{issue_id}/title/undo?sync_id={uuid}
GET  /api/v1/tenants/{slug}/audit
GET  /api/v1/tenants/{slug}/audit/verify
POST /api/v1/webhooks/github
```

Issue title undo restores only the local copy. GitHub remains the source of
truth, so a later sync can apply the GitHub title again.

## Privacy Boundary

The system processes GitHub collaboration metadata only. It never reads or stores source code, diffs, patches, blobs, comment bodies, or commit bodies. Findings are team- or module-level; individual scoring and ranking are out of scope.
