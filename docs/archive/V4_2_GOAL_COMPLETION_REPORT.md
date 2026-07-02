# v4.2 Goal Completion Report

## Added

- Offline Git/PR CSV importer.
- Git item risk detection from changed files.
- Git item linking to traceability links.
- Requirement v2/v3 CSV comparison.
- Deeper OpenAPI operation/parameter/status diff.
- Developer workload dashboard.
- Evidence report now includes traceability, requirement diffs and Git evidence.
- UI exposes all new goal-completion tools.

## Why offline import instead of real GitHub sync?

Real GitHub/GitLab sync requires external credentials and live APIs.
This version keeps the app offline-first by supporting CSV exports and manual pasted data.

## New endpoints

```text
POST /api/projects/{project_id}/git-import
GET  /api/projects/{project_id}/git-items
POST /api/projects/{project_id}/requirement-diff
GET  /api/projects/{project_id}/requirement-diffs
POST /api/projects/{project_id}/openapi-deep-diff
GET  /api/projects/{project_id}/workload
```

## Future live integrations

- GitHub/GitLab OAuth
- PR webhook receiver
- Real commit sync
- Full OpenAPI schema diff
- Excel file parser
