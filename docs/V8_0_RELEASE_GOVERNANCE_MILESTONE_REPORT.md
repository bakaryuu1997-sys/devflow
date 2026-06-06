# v8.0 Release Governance Milestone Report

## Goal
Make the release workflow more audit-ready without adding dependencies or expanding the database unnecessarily.

## Completed
- Added release governance readiness API.
- Added migration notes API/export.
- Added governance UI buttons and renderer.
- Connected governance view to sign-off gate, plan recommendation, scope audit, and migration notes.
- Kept Markdown export support through `content` fields.

## New APIs
- `GET /api/projects/{project_id}/release-governance-readiness`
- `GET /api/release-governance/migration-notes`

## Notes
v8.0 is a milestone/polish release. It does not add a new database table. It documents the migration-sensitive fields/tables added across the v7 governance track.
