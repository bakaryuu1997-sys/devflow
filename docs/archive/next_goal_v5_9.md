# v5.9 Goal — Requirement Quick Management UI

## Scope

Keep this phase small and practical.

## Tasks

- Create requirement from UI for the current selected project.
- List requirements for the current selected project.
- Allow choosing priority.
- Allow choosing status.
- Refresh traceability after creating a requirement.
- Keep no-dependency rule.
- Keep files under 200 lines.

## Acceptance Criteria

```text
quality_check: PASS
compileall: PASS
pytest: PASS
security_check: PASS with local warning
HTTP smoke: PASS
file-size rule: PASS
```

## Out of Scope

- Requirement edit/delete UI.
- Requirement-to-WorkItem linking UI.
- Bulk import UI.
- React/TypeScript migration.
- New dependencies.
