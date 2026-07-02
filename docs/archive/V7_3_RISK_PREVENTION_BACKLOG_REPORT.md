# v7.3 — Risk Prevention Backlog Report

## Scope

Convert recurring risk trends from v7.2 into a concrete prevention backlog and allow one-click creation of release learning items.

## Changes

- Added `app/release_prevention_backlog_service.py`.
- Added `app/routes_v73.py`.
- Added `GET /api/projects/{project_id}/risk-prevention-backlog`.
- Added `POST /api/projects/{project_id}/risk-prevention-backlog/auto-create`.
- Added UI button `Risk Prevention Backlog`.
- Added auto-create action for recurring-risk learning items.
- Added duplicate protection by `source = recurring-risk:<rule_id>`.

## Design note

The backlog uses existing `ReleaseLearningItem` records instead of adding a new table. This is deliberate: prevention items are part of the learning loop, so saving them in the existing learning item table keeps the release flow small and testable.
