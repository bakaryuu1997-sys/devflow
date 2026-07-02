# v6.2 Requirement Edit/Archive UI + Per-Requirement Risk Visibility

## Goal

Make Requirement management usable after initial creation. A real project needs to adjust requirements, archive old ones, and see why each requirement is risky without reading one large raw risk list.

## Completed

- Added `RequirementUpdate` schema.
- Added `PATCH /api/requirements/{requirement_id}`.
- Added `POST /api/requirements/{requirement_id}/archive`.
- Added Requirement-card title editing.
- Added Requirement-card priority/status editing.
- Added Requirement-card archive action.
- Added per-Requirement risk summary on each Requirement card.
- Added `View requirement risks` action that refreshes risk scan and shows only selected Requirement risks.
- Updated risk scan to skip archived Requirements.
- Updated dashboard requirement count to count active Requirements only.
- Updated WorkItem Requirement dropdowns to hide archived Requirements.
- Added v6.2 tests.

## Design choice

Archive is implemented as `status = "Archived"` instead of a new database column. This keeps the change small, avoids migration complexity, and fits the current local/demo SQLite setup.

## Files changed

- `app/schemas_core.py`
- `app/routes_core.py`
- `app/services.py`
- `static/requirement_ui.js`
- `static/requirement_ui.css`
- `static/workitem_ui.js`
- `tests/test_v62_requirement_edit_archive_risk_visibility.py`
- `VERSION.md`
