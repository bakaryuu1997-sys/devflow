# v9.5 Self Evaluation

## What improved

The app can now persist public-key verifier output as evidence instead of only running a dry-run.

## What remains limited

The verified-signature gate is still policy-light. It checks verified evidence exists, but does not yet deeply integrate with immutable evidence manifests.

## Next step

v9.6 should harden the gate by tying verified signature evidence to the current frozen manifest and approval workflow.
