# v6.8 Self-Evaluation

## What is solid

- The release review flow now continues after sign-off.
- Approval history can be compared without adding dependencies.
- Retrospective notes are persisted and exportable.
- The feature is covered by focused tests.

## Trade-off

Approval comparison currently parses the approval Markdown snapshot. This is acceptable for a small, safe v6.8 step because v6.7 already stores the approval record as Markdown. A future version can store structured snapshot JSON if comparison needs to become richer.

## Risk

The UI uses simple prompts for retrospective entry. This is fast and stable, but a future version should replace it with a proper form for longer notes.

## Next step

v6.9 should turn retrospective action items into a prevention checklist for the next release.
