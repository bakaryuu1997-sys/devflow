# v7.2 Self-Evaluation

## What improved

- Structured sign-off snapshots now include richer risk-event details.
- Recurring risk trends can identify repeated `rule_id` patterns across multiple snapshots.
- UI exposes the new analytics without adding dependencies.
- Backward compatibility is preserved for v7.0 structured snapshot tests.

## What is intentionally limited

- Trend analytics is deterministic and rule-based.
- It analyzes stored sign-off snapshots, not every intermediate risk scan.
- Legacy Markdown-only sign-offs can still be opened, but they do not provide rich risk-event history.

## Next best step

v7.3 should convert recurring-risk trends into a prevention backlog and optionally create saved learning items from the top repeated patterns.
