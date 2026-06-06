# v7.9 Release Plan Recommendation Report

## Scope

v7.9 adds a release plan recommendation engine and a scope decision audit trail.

## Completed

- Added recommendation API: `GET /api/projects/{project_id}/release-plan-recommendation`.
- Added audit API: `GET /api/projects/{project_id}/scope-decision-audit`.
- Added `ScopeDecisionAudit` model.
- Updated scope adjustment to record old status, new status, reason, and timestamp.
- Added UI actions for Plan Recommendation and Scope Audit.
- Added Markdown export content for both views.

## Design choice

The recommendation engine is deterministic and reuses v7.8 scenario outputs. This avoids AI ambiguity and keeps the app easy to test locally.
