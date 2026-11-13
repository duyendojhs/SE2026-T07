# Change log

## Scope

- **Related task:** [GitHub Issue #8](https://github.com/duyendojhs/SE2026-T07/issues/8),
  frontend scaffold and responsive shell.
- **Repository acceptance sources:** [Issue #8](https://github.com/duyendojhs/SE2026-T07/issues/8),
  [Build Contract](../../BUILD-CONTRACT.md), and
  [Task 8 repository record](../../tasks/08-frontend-refactor.md).
- **Baseline:** `e6db95fad72da831aecd633ca96e2177fd511868` — branch HEAD before
  this follow-up; the working tree included uncommitted WIP.
- **Archive source:** `6cc63d7f0f2fe4c279f0ca4b9496cbb1d80631da`.

## Changes by commit

| Commit                                                                                                                                                                                              | Purpose and paths                                                                                                                                                                                                                                                                                                | Behavior retained                                                                                                                                                                     | Tests and evidence                                                                                                                                                                                                                                                                                                                                                                                             |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`62568c4f235dd3f5d04b358297af8c52b6c8fc7f`](https://github.com/duyendojhs/SE2026-T07/commit/62568c4f235dd3f5d04b358297af8c52b6c8fc7f) — `refactor(frontend): separate analytics domain contracts`  | Added `frontend/src/domain/analytics`; returned Dashboard fixture/types/model to `features/dashboard`; moved Heatmap period projection into `features/heatmap`; changed route imports to domain contracts; passed telemetry to generic shell through a slot; added domain, heatmap, slot, and stale-route tests. | `/`, `/heatmap`, `/stale-alerts`, `/audit-logs`; legacy `/collaboration-heatmap` redirect; fixture content and 3/7-day filter behavior; mobile drawer interactions; privacy boundary. | [verification matrix](verification-evidence.md); [domain tests](../../../frontend/src/__tests__/analytics-domain.test.ts); [Dashboard tests](../../../frontend/src/__tests__/dashboard-model.test.ts); [Heatmap tests](../../../frontend/src/__tests__/heatmap-model.test.ts); [shell tests](../../../frontend/src/__tests__/AppShell.test.tsx); [page tests](../../../frontend/src/__tests__/pages.test.tsx). |
| [`7ffb27d6b8cb688c15ea078ac2efc76ce856df24`](https://github.com/duyendojhs/SE2026-T07/commit/7ffb27d6b8cb688c15ea078ac2efc76ce856df24) — `docs(frontend): restore legacy task 8 documents verbatim` | Restored `frontend/docs/README.md`, `frontend/docs/architecture.md`, and `frontend/docs/tasks/008-frontend-scaffold.md`; added `frontend/docs/archive-index.md`.                                                                                                                                                 | Restored copies remain historical records; current root `docs/` pages were not changed.                                                                                               | Each restored blob hash matches its path at source commit `6cc63d7`; see the hash table below. Archive index formatting check passed.                                                                                                                                                                                                                                                                          |

The supplemental decision/evidence documents in this directory are committed
separately from code and archive restoration. Their commit SHA is recorded in
the final repository history and completion report; no GitHub issue state or
remote branch is changed here.

## Verbatim archive evidence

| Restored path                                  | Source commit blob                         | Verification                    |
| ---------------------------------------------- | ------------------------------------------ | ------------------------------- |
| `frontend/docs/README.md`                      | `ca819794c71b13a506da28f216d912f744956998` | Working-tree blob hash matched. |
| `frontend/docs/architecture.md`                | `ed268cc1fbf4d971a0a40cf672fdc1fc52397571` | Working-tree blob hash matched. |
| `frontend/docs/tasks/008-frontend-scaffold.md` | `d1f69a8c22b52a726d6dd30b67d98567c367225c` | Working-tree blob hash matched. |

The originals were restored with Git from source commit
[`6cc63d7`](https://github.com/duyendojhs/SE2026-T07/commit/6cc63d7f0f2fe4c279f0ca4b9496cbb1d80631da).
No banner, link correction, or other edit was applied to those three files.
