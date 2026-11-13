# Documentation clarifications

## Purpose and reading order

This note records verified differences between older frontend documents and
the committed frontend code. It supplements the original documents without
editing them. The code paths below describe the implementation present in
commit [`62568c4`](https://github.com/duyendojhs/SE2026-T07/commit/62568c4f235dd3f5d04b358297af8c52b6c8fc7f),
which remains the code baseline for this documentation follow-up.

Read the [current frontend architecture](../architecture.md) and
[Task 8 refactor record](../../tasks/08-frontend-refactor.md) for their
original scope and decisions, then use the clarifications below where those
statements describe an earlier code state. The files under `frontend/docs/`
are preserved historical copies from source commit
[`6cc63d7`](https://github.com/duyendojhs/SE2026-T07/commit/6cc63d7f0f2fe4c279f0ca4b9496cbb1d80631da);
their [archive index](../../../frontend/docs/archive-index.md) explains their
status. Do not treat their old file trees or task-time verification as checks
of the later code snapshot.

## Verified differences

### 1. Heatmap rows represent event types, not roles

- **Older document:** [Current architecture, section 2](../architecture.md)
  describes `HeatmapTable` as a matrix “theo ngày & vai trò” (by day and role).
- **What that wording suggests:** Each row is a team role.
- **Current code:** The table columns are activity days. Its rows are `Commits`,
  `PRs opened`, `PRs merged`, and `Reviews`; each cell displays that event
  count for the day.
- **Evidence:** [HeatmapTable](../../../frontend/src/features/heatmap/components/HeatmapTable.tsx),
  [row definitions](../../../frontend/src/features/heatmap/model.ts),
  [shared activity contract](../../../frontend/src/domain/analytics/types.ts),
  and [Heatmap model tests](../../../frontend/src/__tests__/heatmap-model.test.ts).
- **How to read the older text:** Treat “role” as an earlier documentation
  mismatch. The table is event-by-day and does not group activity by people or
  role.

### 2. The progressbar role belongs to the quota gauge

- **Older document:** [Current architecture, section 6](../architecture.md)
  says metric elements and quota progress both have `role="progressbar"`.
- **What that wording suggests:** Every dashboard metric is exposed as a
  progress bar.
- **Current code:** Dashboard metric cards render as articles with labeled text
  values. The quota gauge uses `role="progressbar"` only when quota values are
  valid; its unavailable state is plain text.
- **Evidence:** [MetricsGrid](../../../frontend/src/features/dashboard/components/MetricsGrid.tsx)
  and [RateLimitGauge](../../../frontend/src/features/telemetry/components/RateLimitGauge.tsx).
- **How to read the older text:** Apply the progressbar accessibility claim to
  the quota gauge only. Dashboard metrics are not progress bars.

### 3. API configuration does not mean the frontend connects to the backend

- **Older document:** [Frontend README, “Cài đặt và cấu hình”](../../../frontend/README.md)
  says the application connects to `http://localhost:8000` by default through
  centralized configuration.
- **What that wording suggests:** The application sends backend requests at
  that URL by default.
- **Current code:** `env.ts` selects `NEXT_PUBLIC_API_URL` or the local fallback,
  and `api.ts` builds endpoint strings. Those values are configuration only;
  a source search finds no `fetch`, `axios`, `XMLHttpRequest`, `ky`, or
  `http.request` use in `frontend/src/`. The Dashboard and detail routes use
  the offline Dashboard fixture, while the root layout supplies the sample
  quota.
- **Evidence:** [environment config](../../../frontend/src/shared/config/env.ts),
  [API route map](../../../frontend/src/shared/config/api.ts),
  [Dashboard fixture adapter](../../../frontend/src/features/dashboard/data.ts),
  [telemetry fixture adapter](../../../frontend/src/features/telemetry/data.ts),
  [Dashboard route](../../../frontend/src/app/page.tsx), and
  [root layout](../../../frontend/src/app/layout.tsx).
- **How to read the older text:** Interpret it as URL configuration prepared
  for later integration, not as a claim that requests are implemented. The UI
  remains fixture-backed.

### 4. Shared range contracts and Dashboard logic now have separate owners

- **Older document:** [Current architecture, section 2](../architecture.md)
  labels `features/dashboard/model.ts` as containing range parsing, median, and
  Dashboard selection logic.
- **What that wording suggests:** The Dashboard model owns the shared URL-range
  parser.
- **Current code:** `parseDashboardRange` is in the plain TypeScript
  `domain/analytics` module and is used by the route pages. Dashboard-specific
  types and aggregation remain in `features/dashboard/model.ts` and
  `features/dashboard/types.ts`.
- **Evidence:** [domain range parser](../../../frontend/src/domain/analytics/range.ts),
  [domain exports](../../../frontend/src/domain/analytics/index.ts),
  [Dashboard model](../../../frontend/src/features/dashboard/model.ts), and
  [Dashboard route](../../../frontend/src/app/page.tsx).
- **How to read the older text:** Its model description predates the boundary
  follow-up. Use the current code paths and
  [architecture decisions](architecture-decisions.md) for ownership today.

### 5. Not every feature has its own fixture adapter or type/model files

- **Older document:** [Task 8 refactor record, Part II, D08 and D10](../../tasks/08-frontend-refactor.md)
  describes every feature as packaging `components/`, `model.ts`, `types.ts`,
  `data.ts`, and `index.ts`, and describes fixture adapters generically as
  `features/*/data.ts`.
- **What that wording suggests:** Each feature owns a complete, parallel set
  of those files.
- **Current code:** Dashboard owns its fixture adapter, types, and model;
  Telemetry owns a quota fixture adapter. Heatmap has a period model and
  components, while Stale Alerts has components. Both detail routes import
  `sampleDashboard` from Dashboard and pass its activity or alerts into their
  feature views. Shared contracts used across Dashboard, Heatmap, and Stale
  Alerts live in `domain/analytics`.
- **Evidence:** [Dashboard files](../../../frontend/src/features/dashboard/),
  [Telemetry adapter](../../../frontend/src/features/telemetry/data.ts),
  [Heatmap module](../../../frontend/src/features/heatmap/),
  [Stale Alerts module](../../../frontend/src/features/stale-alerts/),
  [Heatmap route](../../../frontend/src/app/heatmap/page.tsx), and
  [Stale Alerts route](../../../frontend/src/app/stale-alerts/page.tsx).
- **How to read the older text:** D08/D10 record the earlier refactor plan and
  implementation state. They are not a requirement that every current feature
  has identical files; see the current architecture decisions for the final
  ownership boundaries.

### 6. The archived frontend tree is a historical snapshot

- **Older document:** [Archived frontend architecture, section 2](../../../frontend/docs/architecture.md)
  presents `src/components/`, `src/types/`, `src/mocks/`, and `src/lib/` as the
  structure of that document’s “current” frontend.
- **What that wording suggests:** Those directories describe the current
  checkout.
- **Current code:** The app is organized under `src/app/`, `src/domain/`,
  `src/features/`, and `src/shared/`. The archived three files were restored
  verbatim from commit `6cc63d7`; the subsequent refactor and boundary follow-up
  changed the source organization.
- **Evidence:** [current domain module](../../../frontend/src/domain/analytics/index.ts),
  [Dashboard feature](../../../frontend/src/features/dashboard/index.ts),
  [shared layout](../../../frontend/src/shared/components/layout/index.ts),
  and [archive index](../../../frontend/docs/archive-index.md).
- **How to read the older text:** Read the archived tree as the source-commit
  snapshot that it records, not as a live directory map. The files remain
  unchanged by design.

### 7. Archived browser notes do not establish current viewport QA

- **Older document:** [Archived Task 8 record, section 6](../../../frontend/docs/tasks/008-frontend-scaffold.md)
  records a browser check of the Heatmap URL, old-route redirect, range filter,
  and mobile menu for the version then under review.
- **What that wording might suggest:** The current refactored code has passed
  desktop and mobile viewport inspection.
- **Current evidence:** The follow-up verification record explicitly marks
  visual QA at 1440×900 and 390×844 as **not verified**; no screenshot was
  captured. The earlier task note remains a record of its own review context.
- **Evidence:** [verification evidence, browser QA row](verification-evidence.md)
  and the [archived Task 8 record](../../../frontend/docs/tasks/008-frontend-scaffold.md).
- **How to read the older text:** Keep its historical claim scoped to the
  version and checks recorded there. It is not evidence of viewport QA for the
  current code snapshot.

## Scope note

These clarifications describe the frontend state only. They do not add API
integration, alter the preserved documents, or claim a new visual browser or
CI check. Current viewport QA and a linked CI run remain unverified as recorded
in [verification evidence](verification-evidence.md).
