# v11.6 Operator Final Package

# v11.6 Final Packaging Cleanup

Status: Final package cleanup blocked
Release candidate: `demo-rc-v11.5`
Profile: core-risk

## Checks
- PASS: readme-current — README names the current version.
- PASS: version-current — VERSION.md is current.
- PASS: requirements-present — requirements.txt is present.
- PASS: docs-present — v11.6 docs are present.
- PASS: no-new-destructive-path — v11.6 only packages and verifies installation.
- BLOCK: rc-freeze-ready — v11.5 RC freeze is still ready.

## Cleanup Notes
- Keep v11.5 as the release candidate label.
- Ship v11.6 as the beginner-friendly final package cleanup layer.
- Prefer small verification commands over a huge all-at-once test run.


# v11.6 Beginner Install Verification

Status: Beginner install verification ready

## Steps
1. Create a virtual environment.
2. Install dependencies from requirements.txt.
3. Run the FastAPI app with uvicorn.
4. Open http://localhost:8000 and build the core-risk sample project.
5. Run the v11.6 final package export script.

## Verification Commands
- `python -m venv .venv`
- `.venv\Scripts\activate`
- `pip install -r requirements.txt`
- `python -m compileall app scripts`
- `pytest tests/test_v116_final_packaging_install.py`
- `python scripts/export_v11_6_operator_final_package.py`
- `uvicorn app.main:app --reload`
