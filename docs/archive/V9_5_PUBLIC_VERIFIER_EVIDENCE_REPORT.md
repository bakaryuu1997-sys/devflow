# v9.5 Public Verifier Evidence Report

## Summary

v9.5 attaches the first real public-key verifier output to release governance evidence and adds a verified-signature approval gate.

## Added

- `public_verifier_evidence_attachments` table.
- Public verifier evidence package API.
- Public verifier evidence attachment/list APIs.
- Verified-signature approval gate API.
- UI actions for Verifier Evidence and Verified Gate.
- CLI exports for package and gate review.

## Safety rules

- No private key storage.
- Verification uses public key material and detached signature evidence only.
- PGP/X.509/RFC3161 real verification remains out of scope.
