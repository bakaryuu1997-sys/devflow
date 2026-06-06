# v12.0 Operator Deployment Package

# v12.0 Baseline Freeze Summary

Status: v11.9 baseline freeze confirmed
Baseline archive: `devflow_guard_v11_9_final_release_tag_portfolio.zip`
Release tag: `devflow-guard-demo-v11.9`
Manifest digest: `5ec565c5ac41929963b4b7f952f1c68588a6040e6f6be2e7fc0d61cfbd416944`

## Checks
- PASS: v11-9-release-tag-ready — Portfolio baseline release tag is ready.
- PASS: release-tag-present — Release tag is stable.
- PASS: manifest-digest-present — Evidence digest is available.
- PASS: no-new-feature-scope — v12.0 is checklist and decision only.

## Non-goals
- No new feature endpoint.
- No destructive reset/restore change.
- No production database migration.


# v12.0 Production Deployment Checklist

Decision: Use v11.9 as portfolio baseline; deploy docs/static first, not full API.

## Hosting Decision
- Local portfolio demo — best: Keeps SQLite, FastAPI, and recovery demo behavior intact.
- Vercel static/docs — good: Good for README, screenshots, quickstart, and portfolio landing page.
- Vercel full API — caution: Needs serverless refactor and stateless data strategy before relying on it.
- FastAPI host — good: Best when the interactive API and SQLite demo need to keep working.

## Local Verification
```bash
python -m venv .venv
```
```bash
.venv\Scripts\activate
```
```bash
pip install -r requirements.txt
```
```bash
python -m compileall app scripts
```
```bash
pytest tests/test_v119_final_release_tag_portfolio.py
```
```bash
uvicorn app.main:app --reload
```

## Vercel Static Checklist
- Publish a static portfolio page that links the v11.9 ZIP and quickstart.
- Do not promise live API behavior unless a backend host is connected.
- Include release tag, manifest digest, and demo script summary.
- Keep screenshots or GIFs small enough for fast loading.

## Full API Deployment Checklist
- Pick a FastAPI-friendly host before exposing the full API demo.
- Set environment variables explicitly and avoid production secrets in ZIP.
- Use a disposable demo database, not real user data.
- Run smoke test and post-restore verification after deployment.

## Acceptance Gates
- v11.9 runs locally on the user's machine.
- Portfolio story can be delivered in under five minutes.
- Static page clearly says whether the API is live or local-only.
- No new feature work starts before deployment feedback is collected.
