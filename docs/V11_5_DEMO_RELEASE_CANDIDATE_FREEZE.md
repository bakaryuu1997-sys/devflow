# v11.5 Demo Release Candidate Freeze

v11.5 freezes the recovery demo as a release candidate and adds an operator acceptance checklist.

## Scope

- Produce a demo release candidate freeze report.
- Confirm evidence, fixture validation, smoke test, and digest lock are ready.
- Provide an operator acceptance checklist with one copyable signoff phrase.
- Export a final operator release candidate package.

## Safety rules

v11.5 does not add a destructive reset or restore endpoint. Real restore remains guarded by the existing v10.8 restore phrase and v10.9 snapshot digest lock.

## API

- `GET /api/release-governance/v11-5-demo-release-candidate-freeze`
- `GET /api/release-governance/v11-5-operator-acceptance-checklist`
- `GET /api/release-governance/v11-5-operator-release-candidate-package`

## CLI

```bash
python scripts/export_v11_5_operator_release_candidate_package.py v11_5_rc.md core-risk
```

## Acceptance checklist

The checklist is ready only when all freeze gates pass. The operator can then copy the signoff phrase:

```text
ACCEPT DEMO RC: demo-rc-v11.5
```
