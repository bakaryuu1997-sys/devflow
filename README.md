# DevFlow Guard v12.0

DevFlow Guard is an offline-first release governance demo. It shows release risk, recovery evidence, digest locks, and operator handoff without relying on a production database.

## Current package

- Version: v12.0
- Baseline: v11.9 portfolio demo
- Final tag: devflow-guard-demo-v11.9
- Focus: production deployment checklist and hosting decision

## Run locally (recommended)

DevFlow Guard is offline-first: it runs great on your own machine with SQLite —
no external database or hosting needed. One command sets up everything (creates
the virtualenv on first run, installs dependencies, seeds a default admin, and
starts the server):

```bash
# Windows
run.bat

# macOS / Linux
./run.sh
```

Then open <http://127.0.0.1:8000>. For local personal use **login is disabled**
— you land straight in the app, and an on-page **How to use** guide walks you
through the workflow.

Want the login screen back? Start with `run.bat --auth` (default admin is
`admin@example.com` / `password123`).

Useful flags: `run.bat --reload` (auto-reload while editing), `run.bat --port 9000`,
`run.bat --auth` (require login).

**One-click desktop shortcut** (Windows): create a Desktop icon that launches the app:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_shortcut.ps1
```

### Manual install (if you prefer step by step)

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python scripts/serve.py         # seeds admin + starts http://127.0.0.1:8000
```

You can also start the server directly (no auto-seed) with the classic command:

```bash
uvicorn app.main:app --reload
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
