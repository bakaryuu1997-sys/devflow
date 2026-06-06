# v10.5 Profile-specific Demo Reset Orchestration

## Purpose

v10.5 turns the profile reset plan into a real, scoped reset flow.
It resets only the selected guided sample project and recreates the
same deterministic profile data through the v10.4 sample builder.

## Approval phrase

Each reset requires the exact phrase:

```text
RESET DEMO PROFILE: <profile_id>
```

Example:

```text
RESET DEMO PROFILE: core-risk
```

## API

- `GET /api/release-governance/v10-5-profile-reset-plan?profile_id=core-risk`
- `POST /api/release-governance/v10-5-execute-profile-reset?profile_id=core-risk&approval=RESET%20DEMO%20PROFILE%3A%20core-risk`
- `GET /api/release-governance/v10-5-operator-reset-package?profile_id=core-risk`

## Guardrails

- Wrong or missing approval phrase blocks execution.
- Reset is project-scoped, not a full database drop.
- Legacy `/api/demo/reset` remains unchanged for old tests and demos.
- Production migration approval gates remain separate.

## Result

A successful reset deletes the selected guided sample project, recreates
its requirements, work items, trace links, and release, then marks the
tutorial profile and sample-builder steps as complete.
