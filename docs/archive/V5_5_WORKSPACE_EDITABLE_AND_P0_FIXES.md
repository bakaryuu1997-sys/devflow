# v5.5 Workspace Editable & P0 Fixes

## Goal

Make the Productivity Workspace more usable and fix the two highest-priority release-risk bugs.

## Workspace improvements

Added:

```text
edit task
delete task
reset workspace state
edit calendar block label
persist calendar blocks in localStorage
persist all workspace state in localStorage
```

## P0 bug fixes

### SQL DELETE false-positive

Before:

```sql
DELETE FROM users WHERE id = 1;
```

could be flagged as `delete_without_where`.

After:

```text
DELETE with WHERE is safe.
DELETE without WHERE is blocking.
```

### Traceability duplicate count

Before:

```text
WorkItem + TraceLink overlap could double-count tasks/tests/bugs.
```

After:

```text
Counts are deduplicated by normalized title/target key.
```

## Tests added

```text
tests/test_v55_p0_fixes.py
```

Covers:

```text
safe DELETE with WHERE
unsafe DELETE without WHERE
traceability duplicate task count
```

## Scope control

No new dependency.
No AI/LLM integration.
No React/TypeScript migration.
No backend database schema change.
