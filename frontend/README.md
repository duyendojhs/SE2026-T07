# GitHub Project Coach frontend

Next.js 14 App Router · TypeScript · Tailwind CSS 3 · Lucide React.
Use Node.js 22 LTS and npm. Run from this directory:

```sh
npm ci
npm run dev
```

Open http://localhost:3000. Production: `npm run build`, then `npm start`.

## Checks

```sh
npm run lint
npm run typecheck
npm run format:check
npm test
npm run build
```

Tests run offline, using fixtures under `../backend/tests/mocks/`. The full
monorepo checkout is required for the sample adapters. Dependency installation
requires npm registry access. Frontend CI runs these checks on configured events.
After changing route structure, run build to regenerate Next.js route types.

## Documentation

- [Documentation index](docs/README.md)
- [Current architecture](docs/architecture.md)
- [Task #8: changes, choices, tradeoffs and validation](docs/tasks/008-frontend-scaffold.md)

Routes: `/`, `/heatmap`, `/stale-alerts`, `/audit-logs`.
The old `/collaboration-heatmap` URL redirects to `/heatmap`.
All analytics/quota are sample data; no backend/GitHub integration is included.

Next.js 14.2.35 is retained for task #8. npm audit reports unresolved framework
and tooling advisories; review a version upgrade before public deployment.
