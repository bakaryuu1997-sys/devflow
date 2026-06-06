# v9.0 Self-evaluation

## What improved

- Evidence bundle hash can now be prepared for external signing/timestamping.
- Operator can export a canonical payload without exposing private keys.
- Timestamp handoff records are stored and can be checked against the current payload.

## Known limits

- No private key management.
- No built-in certificate validation.
- External timestamp token is represented by a token hash/reference, not parsed cryptographic proof.

## Next step

v9.1 should add signed payload import verification and timestamp token evidence attachment.
