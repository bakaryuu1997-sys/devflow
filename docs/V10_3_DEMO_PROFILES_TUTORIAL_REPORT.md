# v10.3 Demo Profiles and Tutorial Progress Report

## Scope

v10.3 adds a small usability layer after the v10.2 first-run wizard.

## Completed

1. Demo profile catalog for `core-risk`, `clean-release`, and `governance-heavy`.
2. Profile reset plan that points operators back to the v10.2 safety check.
3. Persistent tutorial progress tracking in `tutorial_progress`.
4. Operator tutorial package export.
5. UI buttons and CLI exports.

## Safety notes

- The legacy `/api/demo/reset` endpoint remains backward compatible.
- Demo profiles are deterministic planning presets, not production migrations.
- No private key storage was added.
- The v8.5 production migration approval gate remains unchanged.
