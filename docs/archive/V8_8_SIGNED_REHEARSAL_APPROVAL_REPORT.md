# v8.8 Signed Rehearsal Artifact Storage + Final Operator Approval Record

## What changed

v8.8 adds an auditable final layer on top of the v8.7 rehearsal workflow.

## Added

- `SignedRehearsalArtifact` table
- `OperatorApprovalRecord` table
- signed rehearsal artifact package endpoint
- signed artifact create/list endpoints
- final operator approval create/list endpoints
- UI for signed package, signed artifacts, and final approval records
- CLI Markdown exports for operator handoff

## Safety stance

The app still does not run production migration automatically from the UI. The real migration CLI remains protected by the exact approval phrase from v8.5.
