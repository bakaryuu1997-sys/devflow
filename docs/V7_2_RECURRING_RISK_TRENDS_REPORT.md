# v7.2 — Richer Risk Event Snapshot Details + Recurring-Risk Trend Analytics

## Scope

v7.2 strengthens release analytics by storing richer risk-event details in structured approval snapshots and using those events to detect recurring risk patterns across sign-off history.

## Completed

- Added per-requirement `risk_events` in structured snapshots.
- Added `risk_event_schema_version: 7.2` while preserving `schema_version: 7.0` compatibility.
- Added project-level recurring-risk trend analytics.
- Added Markdown `content` output for prevention review/export.
- Added UI controls for Recurring Risk Trends.
- Added tests covering snapshot risk events, recurring trend analytics, route registration, and UI controls.

## New API

```text
GET /api/projects/{project_id}/recurring-risk-trends?limit=5
```

## Data captured per risk event

```text
rule_id
title
message
severity
blocking
```

## Why this matters

Earlier analytics could compare risk counts, but it could not reliably explain which risk rule kept returning. v7.2 gives the app a better foundation for release learning and prevention planning.
