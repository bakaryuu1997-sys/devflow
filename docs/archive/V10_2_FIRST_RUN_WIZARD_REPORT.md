# v10.2 First-run Wizard Report

## Scope

v10.2 adds a guided first-run wizard and a safer demo reset workflow for local operators.

## Added

- First-run wizard API and UI entry point.
- Demo reset safety check with workspace inventory.
- Hardened demo reset plan with explicit approval phrase.
- Operator first-run package export.
- CLI exports for wizard, reset safety, and package.

## Safety decisions

- Existing `/api/demo/reset` remains for tests and old demos.
- New v10.2 guided flow documents a safer path before reset.
- No production migration behavior changed.
- No private key storage added.
