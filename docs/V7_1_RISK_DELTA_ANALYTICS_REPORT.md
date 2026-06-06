# v7.1 — Risk Delta Analytics Between Structured Snapshots

## Scope

v7.1 builds on v7.0 structured sign-off snapshots and adds deterministic risk delta analytics between release approval records.

## Added

- New service: `app/release_risk_delta_service.py`
- New route: `app/routes_v71.py`
- New API: `GET /api/projects/{project_id}/release-risk-delta`
- UI control: `Risk Delta`
- UI renderer inside `static/release_snapshot_analytics_ui.js`
- Tests: `tests/test_v71_risk_delta_analytics.py`

## Behavior

The default comparison uses the latest two release sign-off records for a project.

The delta report shows:

- total risk delta
- blocking risk delta
- requirement count delta
- done requirement delta
- worsened requirements
- improved requirements
- added requirements
- removed requirements
- action hints
- Markdown export content in the response payload

## Design Decision

The implementation reads structured JSON snapshots first through `snapshot_from_signoff`. This keeps the analytics stable and avoids brittle Markdown parsing.

No new dependency was added.
