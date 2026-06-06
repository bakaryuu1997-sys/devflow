# v9.3 Signature Adapter Contract Tests Report

v9.3 adds a safer bridge between policy-only signature verification and future real vendor adapters.

## Added

- Adapter contract-test API.
- Sample PGP detached signature fixture.
- Sample X.509/CMS fixture.
- Sample RFC3161 timestamp token fixture.
- Fixture inventory with SHA-256 hashes and private-key marker checks.
- CLI exports for contract tests and fixture inventory.

## Boundary

This version does not perform real PGP, X.509/CMS, or RFC3161 cryptographic verification. It validates the adapter contract, fixture safety, and expected result shape without adding crypto dependencies or private-key storage.
