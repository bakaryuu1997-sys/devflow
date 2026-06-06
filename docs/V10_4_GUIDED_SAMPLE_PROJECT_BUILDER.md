# v10.4 Guided Sample Project Builder

v10.4 adds a safe builder that creates deterministic sample projects from the v10.3 profile catalog without changing the legacy `/api/demo/reset` path.

## Added

- Guided sample project preview endpoint.
- Build endpoint that creates/reuses a named sample project per profile.
- Tutorial completion badge endpoint.
- Operator export package for the builder and badge.

## Guardrails

- The builder does not drop tables.
- Existing sample projects are reused by name to avoid duplicates.
- Profile seeds are separated from service logic for easier future expansion.
