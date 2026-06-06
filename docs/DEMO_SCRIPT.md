# DevFlow Guard End-to-End Demo Script

## Goal

Show that DevFlow Guard is more than a task manager.

It detects release risk across:

```text
Requirements → Tasks → API → Tests → Bugs → Git evidence → Release readiness
```

## 1. Start the app

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000
```

## 2. Reset demo

Click:

```text
Reset Demo
```

This creates:

- demo project
- admin account
- requirement REQ-001
- linked task, API, test, bug and commit
- release 1.0.0

## 3. Review dashboard

Click:

```text
Today Focus
Dashboard
```

Explain:

```text
The app shows release blockers and next actions, not just tasks.
```

## 4. Upload release artifacts

Use files from `examples/`:

```text
dangerous_migration.sql
app_errors.log
test_report_failed.xml
openapi_before.json
openapi_after.json
```

Run:

```text
Scan SQL
Scan Logs
Scan Tests
Scan API Diff
```

## 5. Traceability

Click:

```text
Traceability Matrix
```

Explain:

```text
The app shows whether each requirement has linked tasks, APIs, tests, bugs and commits.
```

## 6. Requirement impact

Use the default example:

```text
REQ-001
Login by email
→ Login by email or phone number
```

Click:

```text
Record Requirement Change
Run Impact Analysis
```

Explain:

```text
A changed requirement can affect API, UI, tests, bugs and release readiness.
```

## 7. Risk control extras

Run:

```text
Code Change Risk
Environment Guard
Requirement Diff
Deep OpenAPI Diff
Workload Dashboard
```

Explain:

```text
These tools replace manual guesswork with deterministic checks.
```

## 8. Advanced readiness

Click:

```text
Advanced Readiness
```

Explain:

```text
The app gives a release decision with blockers, warnings and recommendations.
```

## 9. Evidence report

Click:

```text
Evidence Report
```

Show:

- readable evidence cards
- raw markdown debug
- copy markdown
- download markdown

## 10. Security checklist

Open:

```text
/api/security/checklist
```

Explain:

```text
Local mode allows demo defaults but production mode blocks unsafe secrets and settings.
```


## Demo success criteria

The demo is successful when:

```text
Reset demo works
Login works
Artifact scans return findings
Traceability returns requirement links
Impact analysis returns affected items
Risk extras return deterministic results
Advanced readiness returns release status
Evidence report opens and exports markdown
Security checklist opens
Auth audit returns login activity
```
