# v6.9 Release Learning Loop Report

## Scope

v6.9 adds a practical feedback loop after release sign-off and retrospective review. The app now converts lessons and repeated risk signals into a prevention checklist for the next release.

## Added

- `GET /api/projects/{project_id}/release-learning-loop`
- `POST /api/projects/{project_id}/release-learning-items`
- `PATCH /api/release-learning-items/{item_id}`
- New `ReleaseLearningItem` table
- New deterministic learning service
- New UI script: `static/release_learning_ui.js`
- New UI actions: Learning Loop and Prevention Checklist

## Behavior

The learning loop collects:

1. Retrospective action items
2. Retrospective improvement notes
3. Current recurring requirement-level risk signals
4. Saved prevention checklist items

It produces a Markdown checklist that can be reused in release review evidence.

## Design choice

The implementation stays deterministic and local-first. It does not use AI or external services. This keeps the feature testable, stable, and dependency-free.
