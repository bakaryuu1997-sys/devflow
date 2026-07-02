# v8.9 Self Evaluation

## What improved

Evidence bundles can now be hashed, frozen, listed, and verified after export. This closes the gap between text attestation and tamper-evident release evidence.

## Intentional limit

The manifest is immutable by convention and no update endpoint is provided. It is not yet backed by cryptographic signing or external timestamping.

## Next likely step

Add cryptographic signing or external trusted timestamp support if the workflow needs stronger compliance evidence.
