# v5.7 WorkItem Quick Management UI

## Goal

Make DevFlow Guard more usable by allowing the user to manage Task/Test/Bug items directly from the UI.

## Added

```text
static/workitem_ui.js
static/workitem_ui.css
tests/test_v57_workitem_management.py
```

## UI changes

Added a Step 5 panel:

```text
Quick Work Items
```

The panel supports:

```text
Create task/test/bug
Choose status
Choose severity
Refresh list
Update status from list
```

## Data behavior

New work items are attached to the currently selected project by using:

```text
projectPath("/work-items")
```

This means the panel respects the project selector added in v5.6.

## Scope control

No new dependency.
No database schema change.
No large UI rewrite.
No AI/LLM integration.
