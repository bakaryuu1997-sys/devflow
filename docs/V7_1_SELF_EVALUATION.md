# v7.1 Self-Evaluation

## What improved

- Release analytics can now show whether risk improved or worsened between structured sign-off snapshots.
- Requirements with increased risk are highlighted directly.
- The report includes deterministic action hints instead of vague dashboard text.

## What was intentionally not added

- No new database table.
- No AI-generated analytics.
- No dependency additions.
- No deep historical forecasting.

## Next limitation to address

The snapshot schema still stores summarized risk counts, not full risk event history per requirement. A future version should store richer risk detail snapshots for deeper recurring-risk analytics.
