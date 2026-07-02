# v6.7 Final Release Sign-off Snapshot Report

## Scope

v6.7 adds the final release approval layer after v6.6 requirement-level review completion.

## Completed

- Added `ReleaseSignOff` persistence.
- Added `GET /api/projects/{project_id}/release-signoff-snapshot`.
- Added `POST /api/projects/{project_id}/release-signoffs`.
- Added `GET /api/projects/{project_id}/release-signoffs`.
- Added `GET /api/release-signoffs/{signoff_id}/approval-record`.
- Sign-off is blocked unless all active Requirement done gates pass, all active Requirement reviews are complete, and blocking release risks are zero.
- Approval record exports a Markdown snapshot with project, release, approver, note, risk summary, completion summary, Requirement approval rows, and checklist snapshot.
- UI now exposes Final Sign-off Snapshot and Approval Records.

## Design note

The sign-off record stores a Markdown snapshot instead of recalculating old data later. This is intentional: a final approval record should preserve what was approved at that moment, even if requirements or work items change later.
