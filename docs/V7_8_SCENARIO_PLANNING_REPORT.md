# v7.8 Scenario Planning Report

## Goal

Add release readiness scenario planning and prevention scope adjustment without adding dependencies or a new database table.

## Implemented

- Added scenario planning API for current prevention scope.
- Compared baseline, complete-overdue-first, defer-unscheduled, and fast-track target-window scenarios.
- Added scope adjustment API for prevention items.
- Added Markdown export content for scenario planning and scope adjustment.
- Added UI button and per-item scope action buttons.
- Added tests for API behavior and UI registration.

## Design choice

Scope adjustment uses existing `ReleaseLearningItem.status` values such as `Deferred` and `Out of Scope`. This avoids a migration while still making release-scope decisions explicit.

## Limitations

- Scenario planning is deterministic and rule-based.
- Scope notes are appended to `prevention_action` instead of stored in a dedicated audit table.
- A future version should add structured scope decision history if this becomes a team approval workflow.
