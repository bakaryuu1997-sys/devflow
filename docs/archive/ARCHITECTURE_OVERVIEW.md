# Architecture Overview

## High-level structure

```text
FastAPI backend
SQLite default database
Vanilla HTML/CSS/JS frontend
Offline-first file and CSV import flow
Rule-based risk analysis
Markdown evidence export
```

## Backend layers

```text
routes_*          API layer
*_service.py      business logic
models.py         SQLAlchemy models
schemas_*.py      Pydantic contracts
scripts/          verification and security utilities
```

## Frontend layers

```text
static/index.html             page structure
static/styles.css             base layout
static/flow.css               wizard flow
static/results.css            rich result cards
static/evidence.css           evidence preview
static/api_client.js          API helper
static/ui_state.js            UI state helper
static/result_renderers.js    trace/readiness/finding renderers
static/evidence_renderer.js   evidence renderer
static/flow.js                user workflow actions
```

## Data flow

```text
User action
→ API request
→ service rule engine
→ database record or computed result
→ rich UI renderer
→ optional evidence markdown export
```

## Risk engine examples

SQL migration guard:

```text
DROP TABLE
DROP COLUMN
TRUNCATE
DELETE without WHERE
```

Traceability:

```text
Requirement → Task/API/Test/Bug/Commit
```

Readiness:

```text
Traceability gaps
Requirement changes
Guard findings
Bug patterns
```

Security:

```text
Local mode warnings
Production mode blockers
Login throttling
Auth audit log
```

## Why no AI integration?

This project intentionally uses deterministic rules.

That makes it:

- offline-capable
- easier to test
- predictable in interviews and demos
- different from a ChatGPT wrapper
