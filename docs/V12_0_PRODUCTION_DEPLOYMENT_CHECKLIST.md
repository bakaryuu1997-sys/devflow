# v12.0 Production Deployment Checklist

v12.0 intentionally stops feature growth and uses v11.9 as the portfolio demo baseline.

## Decision

Use v11.9 locally as the full interactive demo. Use Vercel/static hosting for a portfolio landing page, quickstart, release notes, screenshots, and a download link. Do not present the full API as live on Vercel unless a backend deployment decision is made separately.

## Local-first verification

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m compileall app scripts
pytest tests/test_v119_final_release_tag_portfolio.py
uvicorn app.main:app --reload
```

On macOS/Linux, use `source .venv/bin/activate`.

## Vercel/static checklist

- Publish README, quickstart, release tag, and portfolio script.
- Link the v11.9 ZIP and explain that the full API demo is local-first.
- Include manifest digest and checksum handoff summary.
- Avoid implying live database-backed recovery unless a backend host is connected.

## Full API deployment checklist

- Choose a FastAPI-friendly host if interactive API deployment is required.
- Use disposable demo data only.
- Keep restore/reset guardrails unchanged.
- Run smoke-test and post-restore verification after deployment.

## Non-goals

- No new destructive endpoint.
- No production database migration.
- No feature expansion before local demo feedback.
