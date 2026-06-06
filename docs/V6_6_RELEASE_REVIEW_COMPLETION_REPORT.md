# v6.6 — Release review completion tracking + requirement-level done gates

## Scope

v6.6 adds a deterministic release-review completion layer on top of the existing requirement risk dashboard.

## Added

- `GET /api/projects/{project_id}/release-review-completion`
- `GET /api/requirements/{requirement_id}/done-gates`
- `POST /api/requirements/{requirement_id}/review-complete`
- `POST /api/requirements/{requirement_id}/review-reopen`
- New `RequirementReview` table for review-completion tracking.
- Requirement-level done gates:
  - at least one linked task is Done or Closed
  - High/Critical requirements require one Done or Closed test
  - no linked open High/Critical bug
  - no active blocking risk
- Release completion summary:
  - done requirement count
  - reviewed requirement count
  - completion percent
  - review percent
  - blocking requirement count
  - next actions
- UI button: `Release Review Completion`
- Requirement card button: `Done gates`

## Notes

The gates are deterministic and rule-based. This keeps the release review auditable and testable without adding AI dependency or external services.
