# v11.9 Operator Final Release Package

# v11.9 Final Release Tag Preparation

Status: Final release tag preparation ready
Release tag: `devflow-guard-demo-v11.9`
Archive: `devflow_guard_v11_9_final_release_tag_portfolio.zip`
Tag signoff phrase: `TAG RELEASE: devflow-guard-demo-v11.9`
Manifest digest: `d346f4412529ed10b5799548861af1a29d2ef23367f302e4b187ec3ce50f57b9`

## Git Commands
```bash
git status --short
```
```bash
git tag -a devflow-guard-demo-v11.9 -m "TAG RELEASE: devflow-guard-demo-v11.9"
```
```bash
git show devflow-guard-demo-v11.9 --stat
```

## Checks
- PASS: v11-8-handoff-ready — Signed checksum handoff is ready.
- PASS: manifest-digest-present — Manifest digest is locked.
- PASS: handoff-signature-present — Handoff signature is present.
- PASS: no-new-destructive-path — v11.9 only prepares release tag and demo script.


# v11.9 Portfolio Demo Script

Title: DevFlow Guard recovery-governed release demo
Release tag: `devflow-guard-demo-v11.9`

## Demo Flow
- 30s — Open with the problem: Show that release demos fail when reset and restore paths are unsafe.
- 60s — Show guarded recovery: Walk through reset phrase, restore phrase, digest lock, and audit trail.
- 60s — Prove evidence: Display manifest digest d346f4412529... and checksum handoff.
- 30s — Finish with quickstart: Run install verification and explain the final release tag.

## Talk Track
- This project is not a generic task tracker; it is a release safety demo.
- Every risky recovery operation requires explicit operator intent.
- The final ZIP has a manifest digest, handoff signature, and repeatable quickstart.
- The portfolio story is reliability: evidence first, destructive actions locked down.

## Verification Commands
```bash
python -m compileall app scripts
```
```bash
pytest tests/test_v119_final_release_tag_portfolio.py
```
```bash
python scripts/export_v11_9_final_release_package.py
```
