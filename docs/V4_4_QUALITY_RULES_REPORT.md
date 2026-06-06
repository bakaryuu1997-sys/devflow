# v4.4 Quality Rules Report

## Goal

Apply the user's engineering rules slowly and safely.

This version intentionally avoids adding large new features. It focuses on keeping the package stable and easier to control.

## Added

- `rules.md`
- `scripts/quality_check.py`
- `static/api_client.js`
- `static/ui_state.js`
- loading indicator
- better separation between API calls and UI rendering helpers

## Rules addressed

### 1. File size below 200 lines

`quality_check.py` now fails when checked source/docs files exceed 200 lines.

### 2. No business logic inside UI

The UI is still vanilla JavaScript, but API calls and UI state helpers were split out:

```text
static/api_client.js
static/ui_state.js
```

This is not as strong as a React/TypeScript hook architecture yet, but it is cleaner than before.

### 3. Responsive layout

Existing responsive CSS is preserved. This package does not add heavy frontend frameworks.

### 4. No hardcoded secrets

`quality_check.py` scans for common secret patterns.

### 5. Typed contracts

Backend still uses Pydantic schemas. Frontend is not TypeScript yet.

### 6. Loading/error/empty states

Added a global loading indicator and friendlier output helper.

### 7. Avoid heavy dependencies

No new runtime dependency was added.

### 8. Verify before packaging

Verified:

```text
quality_check: PASS
compileall: PASS
pytest: 16 passed
HTTP smoke: PASS
```

## Known limitations

- Frontend is still vanilla JS, not strict TypeScript.
- UI result panels still show structured text/JSON, not rich tables yet.
- Pydantic deprecation warnings remain and should be cleaned in a future step.
