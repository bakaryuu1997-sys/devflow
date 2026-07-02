# v4 Traceability & Impact Analysis Report

## Added

- `goal.md` updated for Project Risk & Release Control System.
- Traceability Matrix.
- Requirement Change Tracker.
- Impact Analysis Engine.
- Code Change Risk Detector.
- Environment Config Guard.
- Bug Pattern Dashboard.
- Advanced Release Readiness.
- UI section for v4 risk-control tools.
- Tests for v4 services and APIs.

## New API endpoints

```text
POST /api/projects/{project_id}/trace-links
GET  /api/projects/{project_id}/trace-links
GET  /api/projects/{project_id}/traceability

POST /api/projects/{project_id}/requirement-changes
GET  /api/projects/{project_id}/requirement-changes
GET  /api/projects/{project_id}/impact/{requirement_key}

POST /api/projects/{project_id}/code-risk
GET  /api/projects/{project_id}/code-risk

POST /api/projects/{project_id}/env-guard
GET  /api/projects/{project_id}/bug-patterns
GET  /api/projects/{project_id}/advanced-readiness
```

## What is real now

The app is no longer just a file scanner.

It now starts building the core chain:

```text
Requirement → Task → API → Test → Bug → Commit → Release
```

## Still future work

- Real GitHub/GitLab API integration.
- Real PR/commit sync instead of manual file path input.
- Deeper OpenAPI field/type diff.
- Real Excel requirement v2/v3 comparison.
- Per-developer workload calculation.
