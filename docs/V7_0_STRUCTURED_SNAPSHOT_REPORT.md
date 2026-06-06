# v7.0 — Structured snapshot storage + stronger release analytics foundation

## Scope

This release adds a machine-readable snapshot layer under the existing final sign-off approval flow.

## What changed

- Added `ReleaseSignOff.snapshot_json` for structured JSON approval snapshots.
- Kept `ReleaseSignOff.snapshot` as the human Markdown approval record.
- Added structured snapshot builder and analytics helpers.
- Added endpoint to open the structured snapshot for a sign-off record.
- Added project-level snapshot analytics endpoint.
- Updated approval compare to prefer structured JSON rows and fall back to legacy Markdown rows.
- Added UI controls for Snapshot Analytics and structured snapshot inspection.

## Why this matters

Before v7.0, compare logic had to parse Markdown approval records. That was acceptable for small steps, but brittle for deeper analytics.

v7.0 creates a safer foundation for future release analytics:

- risk deltas
- requirement trend comparisons
- approval history analysis
- recurring risk detection across releases
- release quality scorecards

## Compatibility

Old Markdown-only approval records are still supported through a legacy fallback parser.

## Dependency policy

No new dependency was added.
