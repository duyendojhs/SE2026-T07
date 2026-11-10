# GitHub Project Coach (SE2026-T07)

An AI-augmented engineering analytics platform designed to detect student collaboration bottlenecks, monitor project velocity, and generate weekly progress summaries using explainable rules and metadata telemetry.

## Team Entropy

- **Do Minh Duyen** (Lead) — System Architecture & GitHub Data Ingestion
- **Ban Khanh Duy** — Analytics, Explainable Rule Engine & LLM Pipeline
- **Truong The Anh** — Frontend Engineering & Data Visualization
- **Hoang Khanh An** — QA Engineering, Security Compliance & DevOps

## Repository Structure

- `backend/` — FastAPI services, rate-limited GitHub client, rule engine, and audit logs.
- `frontend/` — Next.js 14 dashboard skeleton; dashboard features start in S3.
- `docs/` — build contract, architecture decisions, and technical specifications.
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

### Frontend local

```bash
cd frontend
npm install
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
GET  /api/v1/tenants/{slug}/audit
GET  /api/v1/tenants/{slug}/audit/verify
POST /api/v1/webhooks/github
```

## Privacy Boundary

The system processes GitHub collaboration metadata only. It never reads or stores source code, diffs, patches, blobs, comment bodies, or commit bodies. Findings are team- or module-level; individual scoring and ranking are out of scope.
