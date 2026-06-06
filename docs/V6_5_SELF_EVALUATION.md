# v6.5 Self Evaluation

## What went well

- Scope stayed small and practical.
- No dependency or schema migration was added.
- Placeholder conversion is explicit and guarded.
- Checklist export is deterministic and easy to test.
- Existing v6.0-v6.4 workflows still pass.

## Tradeoffs

- Placeholder detection still relies on the generated title pattern because the app does not yet have an `is_placeholder` database field.
- Checklist items are Markdown-only and not yet tracked as completed inside the app.
- Conversion polish uses a browser prompt rather than a dedicated modal.

## Recommended next step

v6.6 should add release review completion tracking and requirement-level done gates, but only after keeping the data model change small and well-tested.
