# Known Limitations

## Production limitations

This release candidate is not a fully production-ready SaaS.

Missing before real production:

- real cloud deployment validation
- external security review
- HTTPS/TLS setup
- backup and restore drill
- production database migration drill
- monitoring provider setup
- multi-instance rate-limit storage
- token blacklist or refresh-token rotation
- password reset flow
- external identity provider

## Auth limitations

- Login throttling is in-memory only.
- Restarting the app resets login attempt counters.
- Logout is audited but does not invalidate already-issued tokens.
- Audit log reuses `ActivityLog` instead of a dedicated auth table.
- No IP/device metadata is captured yet.

## UI limitations

- Frontend is vanilla JavaScript, not TypeScript strict.
- No automated browser screenshot test.
- Result cards are useful but not yet a polished design-system implementation.
- Evidence cards are parsed from markdown instead of structured evidence JSON.

## Integration limitations

- Git/PR import is CSV-based, not live GitHub/GitLab sync.
- Requirement comparison is CSV-based, not full Excel parsing.
- OpenAPI diff is useful but not a complete schema compatibility checker.
- Workload dashboard is basic and not connected to real team calendars or Jira.

## Why this is still valuable

The app is already strong for local/offline demo and portfolio use because it shows:

```text
traceability
release readiness
risk detection
evidence reporting
security hardening
auth audit
```
