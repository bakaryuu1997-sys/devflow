# v6.3 Release Risk Dashboard by Requirement

## Scope

v6.3 keeps the release small and focused. It adds a release-risk dashboard grouped by Requirement and gives concrete fix hints for each risky Requirement.

## Completed

- Added `GET /api/projects/{project_id}/release-risk-dashboard`.
- Dashboard runs the deterministic risk scan and groups active risks by Requirement.
- Archived Requirements are excluded from the dashboard.
- Each Requirement dashboard row includes:
  - Requirement key/title
  - priority/status
  - readiness score
  - total risk count
  - blocking risk count
  - highest severity
  - risk details
  - actionable fix hints
- Added top project-level actions from the riskiest Requirements.
- Added UI button: `Risk Dashboard by Requirement`.
- Added rich UI renderer for release risk by Requirement.
- Kept no-dependency rule.

## Why this matters

Before v6.3, users could see risk events but still had to mentally connect them to what should be fixed first. Now the app gives a clearer release-review view:

```text
Requirement → Risks → Blocking count → Highest severity → Fix hints
```

This makes the app more practical for release readiness and project management.

## Not included

- No AI-generated recommendations.
- No database migration.
- No new dependency.
- No large dashboard redesign.
