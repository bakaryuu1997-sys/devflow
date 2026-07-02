# v5.8 Project and Release Creation UI

## Goal

Make DevFlow Guard more practical by allowing users to create projects and releases directly from the sidebar.

## Added

```text
static/project_creation_ui.js
tests/test_v58_project_release_creation.py
```

## UI changes

The sidebar now has a Create section with:

```text
New project name
Project description
Create project button
New release version
Create release button
```

## Behavior

### Create project

The UI calls:

```text
POST /api/projects
```

Then:

```text
updates context.projectId
refreshes project selector
auto-creates first release if needed
refreshes release selector
```

### Create release

The UI calls:

```text
POST /api/projects/{project_id}/releases
```

Then:

```text
updates context.releaseId
refreshes release selector
```

## Scope control

No new dependency.
No database schema change.
No large UI rewrite.
No AI/LLM integration.
