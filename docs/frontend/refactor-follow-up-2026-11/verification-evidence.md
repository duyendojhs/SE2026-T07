# Verification evidence

## Environment and run identity

- **Local environment:** Windows, PowerShell, `D:\SE\SE2026-T07\frontend`.
- **Node:** `v26.3.1`.
- **npm:** `11.16.0`.
- **Next.js:** `14.2.35`.
- **Commit tested:** `62568c4f235dd3f5d04b358297af8c52b6c8fc7f`.
- **Local run date/time:** 2026-11-13, Asia/Bangkok (UTC+07:00). The final
  Vitest run began at 22:05:39 local time; lint, typecheck, and format checks
  preceded it, and build followed in the same acceptance sequence.
- **Evidence type:** local commands and local HTTP responses. No CI run/link is
  available for this commit.

## Acceptance summary

| Acceptance criterion                                                       | Status           | Evidence details                                  |
| -------------------------------------------------------------------------- | ---------------- | ------------------------------------------------- |
| Shared contracts are pure and consumed without feature-to-feature imports. | Verified locally | [Shared contracts](#1-shared-contracts)           |
| Dashboard model and fixture remain Dashboard-owned.                        | Verified locally | [Dashboard model](#2-dashboard-model-and-fixture) |
| Heatmap keeps the selected 3/7-day activity period.                        | Verified locally | [Heatmap period](#3-heatmap-period)               |
| Telemetry slot crosses root-layout/client-shell composition.               | Verified locally | [Telemetry slot](#4-telemetry-slot)               |
| Routes and redirect retain expected responses.                             | Verified locally | [Routes and redirect](#5-routes-and-redirect)     |
| Automated frontend acceptance suite passes.                                | Verified locally | [Automated checks](#6-automated-frontend-checks)  |
| Desktop/mobile shell is visually usable at 1440×900 and 390×844.           | **Not verified** | [Visual viewport QA](#7-visual-viewport-qa)       |
| CI is green for this commit.                                               | **Not verified** | [CI](#8-ci)                                       |

## Detailed evidence

### 1. Shared contracts

- **Implementation:** `frontend/src/domain/analytics/`; Dashboard, Heatmap, and
  Stale Alerts feature modules.
- **Checks:** `src/__tests__/analytics-domain.test.ts`, `npm run typecheck`, and
  dependency import review.
- **Exact result:** Domain contracts and range tests passed; typecheck exited 0;
  no `features/analytics` module remains.
- **Status:** Verified locally.

### 2. Dashboard model and fixture

- **Implementation:**
  `frontend/src/features/dashboard/{types.ts,model.ts,data.ts}`.
- **Checks:** `src/__tests__/dashboard-model.test.ts` and
  `src/__tests__/DashboardView.test.tsx`.
- **Exact result:** Existing median, selected-period totals, 3/7-day filter,
  fixture content, and preview limit assertions passed as part of 29/29 tests.
- **Status:** Verified locally.

### 3. Heatmap period

- **Implementation:** `frontend/src/features/heatmap/model.ts` and
  `src/app/heatmap/page.tsx`.
- **Checks:** `src/__tests__/heatmap-model.test.ts` and Dashboard interaction
  test.
- **Exact result:** 3-day/7-day selection and empty-period cases passed; route
  test retained `/heatmap?range=3d` flow.
- **Status:** Verified locally.

### 4. Telemetry slot

- **Implementation:** `src/app/layout.tsx` and
  `shared/components/layout/{AppShell.tsx,Header.tsx}`.
- **Checks:** AppShell slot test and `npm run build`.
- **Exact result:** Slot assertion passed; Next.js 14.2.35 production build
  compiled and generated all 7 pages.
- **Status:** Verified locally.

### 5. Routes and redirect

- **Implementation:** `src/app/` and `frontend/next.config.mjs`.
- **Checks:** Page and interaction tests; local HTTP GET checks.
- **Exact result:** `/`, `/heatmap`, `/stale-alerts`, `/audit-logs`: HTTP 200.
  `/collaboration-heatmap`: HTTP 308,
  `Location: http://127.0.0.1:3000/heatmap`.
- **Status:** Verified locally.

### 6. Automated frontend checks

- **Implementation:** Frontend app and test suite.
- **Commands:** `npm run lint`; `npm run typecheck`;
  `npm run format:check`; `npm test`; `npm run build`; `git diff --check`.
- **Exact results:** Lint: no ESLint warnings/errors. Typecheck: exit 0. Format:
  all matched files use Prettier style. Tests: 11 files passed, 29 tests
  passed. Build: compiled, generated 7 pages. Diff check: exit 0.
- **Status:** Verified locally.

### 7. Visual viewport QA

- **Requested viewports:** desktop 1440×900 and mobile 390×844.
- **Attempt:** Browser viewport QA was requested through Computer Use; access to
  Cốc Cốc was not approved, then the browser access host reported unavailable.
- **Exact result:** **Not verified in browser.** No screenshot was captured and
  no visual pass is claimed. Automated component/build checks do not establish
  responsive appearance at these viewports.
- **Status:** Not verified.

### 8. CI

- **Expected check:** CI run/link for this commit, using the workflow in
  `.github/workflows/ci.yml`.
- **Exact result:** No CI run or URL was available. The workflow specifies Node
  22; local verification used Node 26.3.1.
- **Status:** Not verified; no CI pass is claimed.

## Scope limitations

- Frontend data still comes from offline fixtures. The new code does not call
  the backend.
- `src/shared/config/api.ts` and `NEXT_PUBLIC_API_URL` define URL configuration;
  their presence does not mean frontend requests are implemented.
- The backend route modules currently provide S1 auth, repository sync, webhook
  ingestion, health/readiness, and audit behavior. Metrics/findings endpoint
  contracts remain to be agreed before analytics integration.
- Browser visual QA is not verified; automated component/build checks are not a
  substitute for the requested mobile and desktop viewport inspection.
- No CI pass, screenshot, push, merge, or issue update is claimed.
