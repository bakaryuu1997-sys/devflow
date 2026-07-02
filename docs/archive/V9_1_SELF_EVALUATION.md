# v9.1 Self Evaluation

## What improved

- v9.0 prepared payloads for external signing and timestamping.
- v9.1 can import and verify signed payload references.
- v9.1 can attach timestamp token evidence to the same payload.

## Tradeoff

Verification is hash/reference based. It does not validate a vendor-specific cryptographic token format yet.

## Next improvement

Add vendor-neutral signature verification adapter stubs without storing private keys in the app.
