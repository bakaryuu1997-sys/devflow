# v11.9 Final release tag preparation + portfolio demo script

v11.9 prepares the demo for final release tagging and portfolio presentation.

## What it adds

- Final release tag preparation for `devflow-guard-demo-v11.9`.
- Tag signoff phrase for operator copy/paste.
- Portfolio demo script with a short talk track.
- Operator final release package export.

## API

- `GET /api/release-governance/v11-9-final-release-tag-preparation`
- `GET /api/release-governance/v11-9-portfolio-demo-script`
- `GET /api/release-governance/v11-9-operator-final-release-package`

## CLI

```bash
python scripts/export_v11_9_final_release_package.py
```

## Safety

v11.9 does not add reset, restore, migration, or destructive execution paths.
Restore remains locked behind the v10.8 restore phrase and v10.9 digest lock.
