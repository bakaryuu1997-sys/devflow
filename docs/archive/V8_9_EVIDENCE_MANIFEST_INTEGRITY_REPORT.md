# v8.9 Evidence Manifest Integrity Report

## Scope

- Add SHA-256 evidence manifest for signed rehearsal artifacts and final operator approvals.
- Add frozen manifest records for immutable evidence checkpoints.
- Add export bundle integrity check comparing current evidence against the latest frozen manifest.
- Add CLI exports for evidence manifest and bundle integrity verification.

## Safety

- No production database migration is executed automatically.
- Real migration gate from v8.5 remains unchanged.
- Hashing is deterministic and uses Python standard library only.
