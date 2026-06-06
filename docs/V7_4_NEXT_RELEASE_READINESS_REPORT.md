# v7.4 — Next Release Readiness Report

## Goal

Turn prevention backlog items into planned work for the next release by adding owner/due-date planning and a readiness view.

## Implemented

- Added `owner` and `due_date` to `ReleaseLearningItem`.
- Extended release learning item creation to accept planning metadata.
- Added `PATCH /api/release-learning-items/{item_id}/planning`.
- Added `GET /api/projects/{project_id}/next-release-readiness`.
- Added deterministic readiness score and status:
  - Ready
  - Planning Needed
  - At Risk
- Added UI controls for:
  - Plan owner/due
  - Next Release Readiness
  - Markdown export

## Design note

The readiness view uses the existing learning/prevention item table instead of creating a new execution table. This keeps v7.4 small and compatible with the v7.3 prevention backlog.
