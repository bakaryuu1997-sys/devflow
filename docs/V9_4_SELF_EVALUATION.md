# v9.4 Self-Evaluation

## What improved

The project now has its first real public-key verifier path while keeping private keys out of the app.

## Tradeoff

The adapter currently supports only Ed25519 fixture verification. PGP, X.509/CMS, and RFC3161 remain separate future adapters.

## Safety

The dependency is optional and isolated. Missing crypto support reports `Unavailable`; it does not break startup.
