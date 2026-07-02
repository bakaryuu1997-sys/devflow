# v9.4 Public-Key Verifier Report

## Summary

v9.4 introduces the first real public-key verification adapter behind an optional dependency boundary. The adapter is intentionally narrow: Ed25519 payload + public key + detached signature verification.

## Completed

- Added `ed25519-public-key` verifier adapter.
- Added optional `cryptography` boundary.
- Added safe fixture files without private keys.
- Added readiness, fixture package, and dry-run verification APIs.
- Added UI and CLI entry points.

## Out of scope

- Private key storage.
- PGP real verification.
- X.509/CMS real verification.
- RFC3161 TSA token parsing.
- Legal-grade digital signature workflow.
