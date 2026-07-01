# DevFlow Guard v12.0

DevFlow Guard is an offline-first release governance demo. It shows release risk, recovery evidence, digest locks, and operator handoff without relying on a production database.

## Current package

- Version: v12.0
- Baseline: v11.9 portfolio demo
- Final tag: devflow-guard-demo-v11.9
- Focus: production deployment checklist and hosting decision

## Beginner install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m compileall app scripts
pytest tests/test_v120_production_deployment_checklist.py
uvicorn app.main:app --reload
```

On macOS or Linux, activate with:

```bash
source .venv/bin/activate
```

## Development & code quality

```bash
# Install dev tooling (ruff + pre-commit) on top of the runtime deps
pip install -r requirements-dev.txt

# Lint and auto-format (config lives in pyproject.toml)
python -m ruff check app scripts tests
python -m ruff format app scripts tests

# Install git hooks so lint/format run automatically before each commit
pre-commit install
```

Route modules (`app/routes_v*.py`) are discovered and wired automatically by
`app/routes.py`; adding a new `routes_*.py` module with a `router` attribute is
enough to expose it — no manual include list to maintain.

## Final demo path

1. Run v11.9 locally and confirm the portfolio demo works.
2. Use v12.0 baseline freeze summary to confirm no feature creep.
3. Use v12.0 production deployment checklist for hosting decisions.
4. Publish a static portfolio page first if using Vercel.
5. Deploy the full API only after choosing a FastAPI-friendly host.

## Useful commands

```bash
# Export the v12.0 deployment package documentation
python scripts/export_v12_0_deployment_package.py

# Check local server and ledger integrity status
python scripts/devflow_cli.py status

# Run a local compliance scan over commits, migrations, and logs
python scripts/devflow_cli.py scan --migrations ./migrations --test-logs pytest.log

# Install the pre-push compliance hook into your git repository
python scripts/devflow_cli.py install-hook

# Start the background directory watcher to auto-sync modifications
python scripts/local_sync_watcher.py --dir .

# Run the complete test suite including new governance checks
pytest
```

## Safety guardrails

v12.0 does not add destructive reset, restore, or migration behavior. Restore remains locked behind the v10.8 restore phrase and v10.9 snapshot digest lock.

## Deployment decision

Use v11.9 as the portfolio demo baseline. Use Vercel/static hosting for the public portfolio page and keep the interactive FastAPI demo local-first until deployment feedback proves a live backend is worth it.
