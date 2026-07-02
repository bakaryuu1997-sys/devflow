# v8.7 Self-Evaluation

## What improved

The production upgrade workflow now has a rehearsal report and a human-readable operator sign-off checklist before the real migration gate.

## What stayed intentionally unchanged

v8.7 does not auto-run production migration. The real production gate still requires the exact approval phrase from v8.5.

## Verification discipline

All test files were covered through grouped pytest runs because the one-shot full suite can hit the execution timeout in this environment.

## Remaining limitation

The sign-off checklist is exported as Markdown and not yet persisted as a signed database record.
