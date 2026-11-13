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

## Acceptance matrix

| Acceptance criterion                                                       | Implementation path                                                                    | Test/check                                                                                                   | Exact local result or evidence                                                                                                                                                                     | Status           |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| Shared contracts are pure and consumed without feature-to-feature imports. | `frontend/src/domain/analytics/`; Dashboard, Heatmap, and Stale Alerts feature modules | `src/__tests__/analytics-domain.test.ts`; `npm run typecheck`; dependency import review                      | Domain contracts and range tests passed; typecheck exited 0; no `features/analytics` module remains.                                                                                               | Verified locally |
| Dashboard model and fixture remain Dashboard-owned.                        | `frontend/src/features/dashboard/{types.ts,model.ts,data.ts}`                          | `src/__tests__/dashboard-model.test.ts`, `src/__tests__/DashboardView.test.tsx`                              | Existing median, selected-period totals, 3/7-day filter, fixture content, and preview limit assertions passed as part of 29/29 tests.                                                              | Verified locally |
| Heatmap keeps the selected 3/7-day activity period.                        | `frontend/src/features/heatmap/model.ts`; `src/app/heatmap/page.tsx`                   | `src/__tests__/heatmap-model.test.ts`; Dashboard interaction test                                            | 3-day/7-day selection and empty-period cases passed; route test retained `/heatmap?range=3d` flow.                                                                                                 | Verified locally |
| Telemetry slot crosses root-layout/client-shell composition.               | `src/app/layout.tsx`; `shared/components/layout/{AppShell.tsx,Header.tsx}`             | AppShell slot test; `npm run build`                                                                          | Slot assertion passed; Next.js 14.2.35 production build compiled and generated all 7 pages.                                                                                                        | Verified locally |
| Routes and redirect retain expected responses.                             | `src/app/`; `frontend/next.config.mjs`                                                 | Page and interaction tests; local HTTP GET checks                                                            | `/`, `/heatmap`, `/stale-alerts`, `/audit-logs`: HTTP 200. `/collaboration-heatmap`: HTTP 308, `Location: http://127.0.0.1:3000/heatmap`.                                                          | Verified locally |
| Automated frontend acceptance suite passes.                                | Frontend app and test suite                                                            | `npm run lint`; `npm run typecheck`; `npm run format:check`; `npm test`; `npm run build`; `git diff --check` | Lint: no ESLint warnings/errors. Typecheck: exit 0. Format: all matched files use Prettier style. Tests: 11 files passed, 29 tests passed. Build: compiled, generated 7 pages. Diff check: exit 0. | Verified locally |
| Desktop/mobile shell is visually usable at 1440×900 and 390×844.           | `src/shared/components/layout/{AppShell.tsx,Header.tsx,Sidebar.tsx}`                   | Browser viewport QA requested; Computer Use attempt                                                          | **Not verified in browser.** Computer Use reported it was not approved for Cốc Cốc; the browser access host then reported unavailable. No screenshot was captured and no visual pass is claimed.   | Not verified     |
| CI is green for this commit.                                               | `.github/workflows/ci.yml`                                                             | CI run/link                                                                                                  | No CI run or URL was available. The workflow specifies Node 22; local verification used Node 26.3.1.                                                                                               | Not verified     |

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
