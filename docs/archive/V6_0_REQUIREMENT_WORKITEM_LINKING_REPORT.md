# v6.0 Requirement to WorkItem Linking UI Report

## Scope completed

- Added a Requirement selector to the WorkItem creation form.
- Added a WorkItem filter by Requirement.
- Added an Unlinked-only WorkItem filter.
- Rendered linked Requirement key/title inside each WorkItem card.
- Refreshed traceability after WorkItem create/status update without forcing step navigation.
- Added backend support for `GET /api/projects/{project_id}/work-items?requirement_id=...`.
- Added backend validation to reject cross-project Requirement links.
- Kept the no-new-dependency rule.

## User value

The app flow is now more realistic:

```text
Project → Requirement → Task/Test/Bug → Traceability → Release Risk
```

This makes release risk more meaningful because work items can be linked to concrete requirements at creation time.

## Files changed

- `static/index.html`
- `static/workitem_ui.js`
- `static/workitem_ui.css`
- `static/requirement_ui.js`
- `static/flow.js`
- `app/schemas_core.py`
- `app/routes_core.py`
- `tests/test_v60_requirement_workitem_linking.py`
- `VERSION.md`

## Notes

- Requirement edit/delete was intentionally not added in this version.
- WorkItem relinking by editing an existing item is supported in the API, but no separate edit UI was added yet.
- The implementation stayed intentionally small to protect stability.
