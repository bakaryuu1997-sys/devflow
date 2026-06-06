# v11.4 Recovery Evidence Bundle + Final Demo Handoff Polish

v11.4 packages the recovery proof into a copy-friendly handoff bundle.
It does not add a new destructive restore endpoint.

## Scope

- Build a recovery evidence bundle from existing v10.6 through v11.3 outputs.
- Show snapshot digest and digest lock in one place.
- Add final demo cards and operator script.
- Export a combined operator demo handoff package.

## Safety

Restore execution remains guarded by the existing controls:

- v10.8 restore phrase: `RESTORE DEMO PROFILE: <profile_id>`
- v10.9 snapshot digest lock
- v10.9 guarded restore endpoint

## Endpoints

`GET /api/release-governance/v11-4-recovery-evidence-bundle?profile_id=core-risk`

`GET /api/release-governance/v11-4-final-demo-handoff-polish?profile_id=core-risk`

`GET /api/release-governance/v11-4-operator-demo-handoff-package?profile_id=core-risk`

## CLI

`python scripts/export_v11_4_operator_demo_handoff_package.py recovery_v11_4.md core-risk`

## Demo handoff checklist

1. Open the v11.4 recovery evidence bundle.
2. Confirm all required evidence sections are ready.
3. Copy the digest lock only from the validated bundle.
4. Use v11.4 handoff polish to explain the workflow.
5. Do not execute restore from v11.4.
