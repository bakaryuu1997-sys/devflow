# v7.6 — Prevention Burndown Analytics + Owner Workload Balance Report

## Goal

Build on v7.5 by making prevention work measurable, not just visible in lanes.

## Added

- `app/release_prevention_analytics_service.py`
- `app/release_prevention_analytics_export.py`
- `app/routes_v76.py`
- `static/prevention_analytics_ui.js`
- `tests/test_v76_prevention_analytics.py`

## APIs

- `GET /api/projects/{project_id}/prevention-burndown-analytics`
- `GET /api/projects/{project_id}/owner-workload-balance`

## Prevention burndown analytics

The burndown view reports:

- total prevention items
- open prevention items
- done/prevented items
- overdue items
- due-soon items
- completion rate
- status counts
- 0/7/14/30-day projected remaining open items
- at-risk item list
- deterministic action hints
- Markdown export content

## Owner workload balance

The workload view groups open prevention work by owner and reports:

- owner count
- average open items per owner
- unassigned open items
- overloaded owner count
- owner status: Balanced, Watch, Overloaded, or Needs Owner
- workload score based on open, overdue, due-soon, and escalated items
- Markdown export content

## Design choice

No new table was added. v7.6 intentionally reuses `ReleaseLearningItem` fields from v7.4/v7.5: status, owner, due date, and created time. This keeps the release analytics deterministic, small, and easy to test.

## Limitation

The app still does not store a real completion timestamp for prevention items. Burndown therefore uses current status and due dates as a planning projection. A future version can add `completed_at` if deeper historical burndown is needed.
