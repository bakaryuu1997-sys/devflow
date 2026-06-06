# v11.2 Recovery Fixture Validation Hardening + Sample Operator Walkthrough

v11.2 hardens the v11.1 fixture workflow before any operator uses a snapshot for restore planning.

## Scope

- Validate fixture version and v10.6 snapshot export version.
- Validate selected profile, payload profile, and snapshot profile all match.
- Recompute the snapshot digest and compare it to the exported digest.
- Verify required restore tables are present.
- Reuse the v10.7 dry-run rehearsal and v10.9 conflict report.
- Add a sample operator walkthrough with copy targets.

## Safety boundary

v11.2 does not add a new destructive restore endpoint. Real restore remains locked behind:

1. v10.8 restore phrase: `RESTORE DEMO PROFILE: <profile_id>`
2. v10.9 snapshot digest lock
3. Existing rehearsal and conflict detection gates

## API

- `POST /api/release-governance/v11-2-fixture-validation-report`
- `GET /api/release-governance/v11-2-sample-operator-walkthrough`
- `GET /api/release-governance/v11-2-operator-walkthrough-package`

## CLI

```bash
python scripts/export_v11_2_operator_walkthrough_package.py v11_2_walkthrough.md core-risk
```

## Operator walkthrough

1. Build or reuse the v10.4 guided sample project.
2. Export the v11.1 fixture example.
3. Run the v11.2 validation report against that exact payload.
4. Confirm the v10.7 rehearsal is ready.
5. Copy the digest only from the validated v11.2 report.
6. Execute restore only through the existing v10.9 guarded path.
