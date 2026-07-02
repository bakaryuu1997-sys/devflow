# v6.1 WorkItem Edit/Relink UI + Requirement Linked Summary Report

## Goal

Make the existing Requirement → WorkItem flow more practical after creation. Users can now correct or move work items without recreating them, and can quickly see how much implementation/test/bug coverage each requirement has.

## Completed changes

### WorkItem UI

- Added inline WorkItem title editing.
- Added inline status editing.
- Added inline severity editing.
- Added inline Requirement relink selector.
- Added support for unlinking a WorkItem from any Requirement.
- Added a shared refresh path after WorkItem changes.

### Requirement UI

- Requirement cards now show linked item summary:
  - total linked items
  - task count
  - test count
  - bug count
- Added a `View linked work items` action that sets the WorkItem Requirement filter.

### Tests

Added `tests/test_v61_workitem_relink_requirement_summary.py` with coverage for:

- moving a WorkItem from one Requirement to another
- traceability count movement after relink
- unlinking a WorkItem from a Requirement
- static UI checks for relink and linked-summary controls

## Dependency policy

No new runtime dependency was added.

## Result

v6.1 improves the app from simple creation flow to correction/editing flow:

```text
Project → Requirement → WorkItem → Edit/Relink → Traceability Refresh → Release Risk
```
