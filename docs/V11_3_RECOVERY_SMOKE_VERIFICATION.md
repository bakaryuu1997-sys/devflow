# v11.3 Recovery Smoke-Test Automation + Post-Restore Verification

v11.3 adds a safe recovery smoke test and a post-restore verification report.
It does not add a new destructive restore endpoint.

## Smoke test automation

The smoke test checks the existing recovery chain:

1. Build or reuse the v10.4 sample profile project.
2. Export a v11.1 fixture.
3. Run v11.2 hardened fixture validation.
4. Run v11.1 import rehearsal in dry-run mode.
5. Confirm the v10.9 digest lock is available.
6. Confirm the v10.9 guarded restore plan is ready.

Endpoint:

`GET /api/release-governance/v11-3-recovery-smoke-test-automation?profile_id=core-risk`

## Post-restore verification

The verification report compares the expected snapshot with current profile rows.
It reports digest match, count match, and available restore/digest-lock audit records.
Audit checks are warnings because a developer may run verification before a real restore.

Endpoint:

`POST /api/release-governance/v11-3-post-restore-verification-report?profile_id=core-risk`

Body: v10.6 `snapshot_export` payload.

## Operator package

Endpoint:

`GET /api/release-governance/v11-3-operator-smoke-verification-package?profile_id=core-risk`

CLI:

`python scripts/export_v11_3_operator_smoke_verification_package.py recovery_v11_3.md core-risk`

## Safety rule

Restore still requires the v10.8 restore phrase and the v10.9 snapshot digest lock.
