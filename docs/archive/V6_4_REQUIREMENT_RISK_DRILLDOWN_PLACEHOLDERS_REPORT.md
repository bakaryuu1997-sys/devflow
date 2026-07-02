# v6.4 Requirement Risk Drilldown + Placeholder Actions Report

## Goal

Make each risky Requirement easier to inspect and fix without leaving the release-risk dashboard.

## Completed

- Added `GET /api/requirements/{requirement_id}/risk-drilldown`.
- Added `POST /api/requirements/{requirement_id}/work-item-placeholders`.
- Drilldown returns Requirement metadata, score, active risks, linked WorkItems, missing placeholders, and next actions.
- Dashboard rows now include a Drilldown button.
- Dashboard rows can create missing task/test placeholders in one click when deterministic rules detect gaps.
- Requirement cards now include a Risk drilldown button.
- Placeholder creation is idempotent and returns an existing linked task/test when one already exists.
- Archived Requirements reject placeholder creation.

## Design Notes

- No database migration was added.
- No dependency was added.
- Placeholder actions are deterministic and rule-based.
- Placeholder titles are explicit so the user knows they still need to replace placeholder work with real implementation or test details.

## Files Updated

- `app/routes_v64.py`
- `app/routes.py`
- `app/release_risk_dashboard_service.py`
- `app/routes_core.py`
- `app/services.py`
- `app/schemas_core.py`
- `static/risk_drilldown_ui.js`
- `static/flow.js`
- `static/result_renderers.js`
- `static/requirement_ui.js`
- `static/index.html`
- `tests/test_v64_requirement_risk_drilldown_placeholders.py`
- `VERSION.md`
- `goal.md`

## Result

v6.4 makes the release-risk dashboard more actionable. The user can now inspect a risky Requirement and create the missing task/test scaffolding immediately.
