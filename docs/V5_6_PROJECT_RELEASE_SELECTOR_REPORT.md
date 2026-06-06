# v5.6 Project/Release Selector + Stepper Flow Fix

## Goal

Fix the practical UI limitation where the frontend was hardcoded to `projectId = 1` and `releaseId = 1`.

## Added

```text
static/project_context.js
static/devflow_init.js
static/context_selector.css
```

## Frontend changes

- Added Project selector in sidebar.
- Added Release selector in sidebar.
- Selected project/release is saved in localStorage.
- Replaced hardcoded frontend constants with dynamic context getters.
- Evidence markdown link is now dynamic.
- Release notes action is now dynamic.
- Goal Completion panel is now inside Step 5.
- `flow.js` remains under 200 lines by moving init/dynamic actions into `devflow_init.js`.

## Backend cleanup

Refactored `api_risks` in `routes_core.py`.

Before:

```text
return list(...) and run_risk_scan(...)
```

After:

```text
requirements = [...]
if not requirements:
    return []
return run_risk_scan(...)
```

## Scope control

No new dependency.
No new database schema.
No large UI rewrite.
No product feature expansion beyond selector and flow correctness.
