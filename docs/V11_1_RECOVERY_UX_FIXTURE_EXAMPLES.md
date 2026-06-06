# v11.1 — Recovery UX polish + export/import fixture examples

v11.1 improves the operator experience around the v10.6-v11.0 recovery flow. It adds copy-friendly recovery cards and example export/import fixture payloads for safe rehearsal.

## Safety model

- v11.1 does not add a new destructive restore path.
- Import fixtures run through the v10.7 rehearsal flow.
- Real restore still requires the v10.8 restore phrase and v10.9 snapshot digest lock.
- Fixture JSON is an operator aid, not an automatic restore job.

## API

- `GET /api/release-governance/v11-1-recovery-ux-summary`
- `GET /api/release-governance/v11-1-export-fixture-example`
- `POST /api/release-governance/v11-1-import-fixture-example`
- `GET /api/release-governance/v11-1-operator-fixture-package`

## CLI

```bash
python scripts/export_v11_1_operator_fixture_package.py v11_1_fixtures.md core-risk
```

## Operator fixture flow

1. Build or reuse the guided sample project.
2. Export the v11.1 fixture example.
3. Paste the fixture into the import fixture rehearsal endpoint.
4. Confirm rehearsal readiness and snapshot digest.
5. Use the normal v10.9 guarded restore flow only if restore is required.

## Boundary

This milestone intentionally avoids automatic import execution. Restore remains a guarded manual operation.
