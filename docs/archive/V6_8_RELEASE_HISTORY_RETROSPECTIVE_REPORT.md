# v6.8 Report — Release Approval History Compare + Post-Release Retrospective Notes

## Scope

v6.8 adds release-learning features after final sign-off:

1. Compare approval records for a project.
2. Show Requirement scope changes between approval snapshots.
3. Save post-release retrospective notes.
4. Export retrospective notes as Markdown.
5. Keep all logic deterministic with no new dependency.

## Backend

Added `app/release_history_service.py`:

- `compare_release_signoffs`
- `create_retrospective_note`
- `list_retrospective_notes`
- `export_retrospective_note`

Added `app/routes_v68.py`:

- `GET /api/projects/{project_id}/release-signoffs/compare`
- `GET /api/projects/{project_id}/release-retrospectives`
- `POST /api/projects/{project_id}/release-retrospectives`
- `GET /api/release-retrospectives/{note_id}/export`

Added model:

- `ReleaseRetrospective`

## UI

Added `static/release_history_ui.js` with:

- Compare latest approval records.
- Create retrospective note.
- List retrospective notes.
- Open retrospective Markdown export.

Updated `static/index.html` with:

- Compare Approvals
- Retrospectives
- New Retrospective

## Design choice

Approval comparison reads the Markdown snapshot created by v6.7. This avoids adding a large schema migration for snapshot JSON while still making history comparison useful and testable.
