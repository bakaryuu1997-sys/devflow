# v6.3 Self Evaluation

## What went well

- The change stayed narrow and practical.
- Risk data is now grouped by Requirement instead of only shown as a flat list.
- Fix hints are deterministic and mapped to known rule IDs.
- Archived Requirements remain excluded from active release-risk views.
- Tests cover the API grouping, archive exclusion, and static UI wiring.

## Risks / limitations

- Fix hints are rule-based, not contextual AI suggestions.
- The dashboard is still simple HTML rendering, not a full analytical dashboard.
- Requirement score is calculated from current deterministic risk events only.

## Next step

```text
v6.4 — Requirement risk drilldown + one-click create missing task/test placeholder
```
