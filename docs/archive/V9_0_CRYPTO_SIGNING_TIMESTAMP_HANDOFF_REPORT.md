# v9.0 — Cryptographic signing readiness + external timestamp handoff

## Completed

- Added cryptographic signing readiness API.
- Added external timestamp handoff package API.
- Added timestamp handoff record storage.
- Added timestamp handoff integrity check.
- Added UI buttons for signing readiness, timestamp handoff, and timestamp integrity.
- Added CLI exports for signing readiness and timestamp handoff package.
- Updated migration checker and dry-run SQL for `external_timestamp_handoff_records`.

## Safety stance

v9.0 does not store private keys and does not perform legal digital signing. It prepares a deterministic SHA-256 payload for external signing or timestamp authority workflows.
