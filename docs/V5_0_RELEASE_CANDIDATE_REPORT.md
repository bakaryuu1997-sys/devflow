# DevFlow Guard v5.0 Release Candidate Report

## Goal

Freeze features and turn DevFlow Guard into a clean portfolio/demo release candidate.

## What changed

No product feature was added.

This release focuses on:

- final README
- end-to-end demo script
- architecture overview
- honest known limitations
- release candidate checklist
- full verification
- clean packaging

## New documentation

```text
README.md
docs/DEMO_SCRIPT.md
docs/ARCHITECTURE_OVERVIEW.md
docs/KNOWN_LIMITATIONS.md
docs/RELEASE_CANDIDATE_CHECKLIST.md
```

## Verification performed

```text
python scripts/quality_check.py
python -m compileall app
pytest
python scripts/security_check.py
HTTP smoke test
```

## HTTP smoke tested

```text
GET  /api/health
GET  /
GET  /docs
GET  /api/security/checklist
POST /api/demo/reset
POST /api/auth/login
GET  /api/auth/me
GET  /api/projects/1/traceability
GET  /api/projects/1/advanced-readiness
GET  /api/projects/1/evidence?release_id=1
GET  /api/projects/1/evidence.md?release_id=1
GET  /api/auth/audit
POST /api/auth/logout
```

## Release candidate rule

From this point, avoid adding new features unless they fix a release-blocking issue.
