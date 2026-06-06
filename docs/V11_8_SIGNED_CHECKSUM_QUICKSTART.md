# v11.8 Signed archive checksum handoff + final quickstart

v11.8 closes the demo release handoff with a signed checksum package and a simple user-facing quickstart.

## Scope

- Reuse the v11.7 archive integrity manifest.
- Publish a stable manifest digest and handoff signature.
- Provide a final quickstart for first-time users.
- Keep the recovery guardrails from v10.8 and v10.9 unchanged.

## Endpoints

- `GET /api/release-governance/v11-8-signed-archive-checksum-handoff`
- `GET /api/release-governance/v11-8-final-user-facing-quickstart`
- `GET /api/release-governance/v11-8-operator-checksum-quickstart-package`

## CLI

```bash
python scripts/export_v11_8_checksum_quickstart_package.py
```

## Safety note

v11.8 does not add any reset or restore execution path. Restore remains locked behind the restore phrase and snapshot digest lock.
