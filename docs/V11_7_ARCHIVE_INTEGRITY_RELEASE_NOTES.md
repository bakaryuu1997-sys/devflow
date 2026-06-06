# v11.7 Archive Integrity Manifest + Release Notes Polish

v11.7 is a final packaging polish layer. It adds an archive integrity manifest and release notes that are useful when handing the demo ZIP to another operator.

## Scope

- Generate a manifest for release-critical files.
- Record file size, line count, and SHA-256 digest.
- Produce polished release notes for the final demo handoff.
- Keep the frozen RC label `demo-rc-v11.5`.
- Avoid any new destructive reset or restore route.

## Endpoints

- `GET /api/release-governance/v11-7-archive-integrity-manifest`
- `GET /api/release-governance/v11-7-release-notes-polish`
- `GET /api/release-governance/v11-7-operator-release-package`

## CLI

```bash
python scripts/export_v11_7_release_package.py
```

## Operator notes

Use the manifest digest as a simple handoff fingerprint. It does not replace a signed release, but it helps detect accidental packaging drift.

Restore execution remains protected by the existing restore phrase and snapshot digest lock.
