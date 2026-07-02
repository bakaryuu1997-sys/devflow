# v4.6 Evidence Report UX Polish

## Goal

Improve the evidence report experience without changing stack or adding dependencies.

## Added

- `static/evidence_renderer.js`
- `static/evidence.css`
- evidence report section cards
- evidence toolbar
- copy markdown action
- preserved markdown download link
- raw markdown debug block

## What changed

Before:

```text
Evidence report appeared as one long text block.
```

After:

```text
Evidence report appears as readable section cards:
- Requirements
- Traceability Links
- Requirement Diffs
- Git Evidence
- Work Items
- Risks
- Guard Findings
- Recent Activity
```

## Export behavior

Markdown export is unchanged:

```text
GET /api/projects/1/evidence.md?release_id=1
```

## Dependency policy

No new dependency was added.

## Scope control

This version does not migrate to React or TypeScript.
It only improves evidence report display.
