# v11.6 Final Packaging Cleanup + Beginner Install Verification

Goal: make the frozen demo package easier for a beginner to install, verify, and hand off.

## Scope

- Verify README, VERSION, requirements, docs, and RC freeze readiness.
- Provide copyable beginner install commands.
- Export one final operator package.
- Keep v11.5 as the frozen release candidate label.

## Safety rule

v11.6 does not add a destructive reset or restore endpoint. Restore remains guarded by the v10.8 restore phrase and the v10.9 snapshot digest lock.

## Beginner commands

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m compileall app scripts
pytest tests/test_v116_final_packaging_install.py
python scripts/export_v11_6_operator_final_package.py
uvicorn app.main:app --reload
```

Open `http://localhost:8000` and use the v11.6 buttons in Step 3.

## Endpoints

- `GET /api/release-governance/v11-6-final-packaging-cleanup`
- `GET /api/release-governance/v11-6-beginner-install-verification`
- `GET /api/release-governance/v11-6-operator-final-package`
