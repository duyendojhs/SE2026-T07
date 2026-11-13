# Next frontend implementation steps

These are planned tasks, not implementation in this scaffold follow-up. They
preserve the Issue #8 boundary: no backend integration or analytics product
feature is added here.

## 1. Agree on the analytics API contract

- **Dependency:** Backend owners define the metrics and findings response
  schema, tenant scope, authentication expectations, freshness, pagination, and
  error behavior. Current backend routes do not expose metrics/findings.
- **Work:** Record an OpenAPI-backed contract and sample payloads that contain
  only approved collaboration metadata. Map each frontend view field to an
  endpoint field; decide 3/7-day range semantics and empty-data meaning.
- **Acceptance:** Contract review is approved by frontend/backend owners;
  schemas and offline examples are checked into the repository; privacy and
  tenant-scope review passes; no API call is added until the contract is stable.

## 2. Add a data-source/service adapter

- **Dependency:** Task 1 contract is accepted.
- **Work:** Define a typed interface for dashboard, heatmap, and stale-alert
  reads. Keep the current fixture adapter as the deterministic offline source;
  add an HTTP adapter only for endpoints in the accepted contract. Keep auth
  secrets out of browser code.
- **Acceptance:** Unit tests use fixtures and make no external HTTP calls;
  adapter tests cover serialization, tenant path, range parameters, and
  redacted errors; typecheck and build pass.

## 3. Define loading, error, and empty states

- **Dependency:** Task 2 establishes the data source and its error types.
- **Work:** Add route-level loading/error boundaries and distinguish no data
  from unavailable data. Retain the existing shell and consistent page layout.
- **Acceptance:** Tests cover loading, error, empty, and populated states for
  each integrated view; keyboard and responsive browser QA pass at mobile and
  desktop viewports.

## 4. Establish auth/session and tenant context

- **Dependency:** Contract review confirms session behavior, tenant identity,
  and authorization/error rules; coordinate with the backend S1 routes.
- **Work:** Resolve tenant context safely on the server, define session expiry
  and logout behavior, and protect tenant-scoped requests. Do not put GitHub or
  session secrets in public client configuration.
- **Acceptance:** Offline tests cover unauthenticated, expired-session,
  authorized, and wrong-tenant cases; server responses and UI reveal no
  cross-tenant data; security/privacy review passes.

## 5. Connect real analytics data

- **Dependency:** Tasks 1–4 are accepted and metrics/findings endpoints exist.
- **Work:** Replace fixture reads through the adapter boundary, preserving the
  existing route and range behavior. Keep deterministic rule evidence and
  metadata-only inputs; do not add individual scoring or source-code analysis.
- **Acceptance:** Contract tests run offline with backend fixtures; integration
  checks verify tenant scoping, 3/7-day filtering, loading/error/empty behavior,
  and the existing privacy boundary. Demo data sources and freshness are
  labeled accurately.
