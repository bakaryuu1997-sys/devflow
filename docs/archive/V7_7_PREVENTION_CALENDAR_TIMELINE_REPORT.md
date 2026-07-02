# v7.7 Prevention Calendar View + Release Readiness Timeline Report

## Goal

Make prevention planning easier to execute by showing prevention items on a due-date calendar and projecting release readiness across near-term checkpoints.

## Implemented

- Added prevention calendar service and Markdown exporter.
- Added release readiness timeline service and Markdown exporter.
- Added v7.7 API routes:
  - `GET /api/projects/{project_id}/prevention-calendar-view`
  - `GET /api/projects/{project_id}/release-readiness-timeline`
- Added UI renderer and buttons for both views.
- Added tests for API behavior, Markdown export, UI wiring, and route registration.

## Design choices

- No new frontend calendar package was added.
- No new database table was added.
- The feature uses existing `ReleaseLearningItem.owner`, `due_date`, and `status` fields from v7.4-v7.6.
- Timeline scoring is deterministic and transparent rather than AI-generated.

## Limitation

The timeline is projection-based. It uses current status and due dates, not historical completion timestamps.
