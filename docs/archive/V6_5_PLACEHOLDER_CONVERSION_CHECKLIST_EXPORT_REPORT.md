# v6.5 Placeholder Conversion + Release Review Checklist Export Report

## Goal

Make v6.4 placeholders more useful by allowing them to become real work items, then give the user a copy-ready release review checklist based on Requirement-level risks.

## Completed

- Added `POST /api/work-items/{item_id}/convert-placeholder`.
- Added `GET /api/projects/{project_id}/release-review-checklist`.
- Added `release_review_checklist_service.py` for deterministic Markdown export.
- Added UI button: `Export Release Review Checklist`.
- Added UI button: `Convert placeholder` inside Requirement risk drilldown linked-item list.
- Added static UI wiring for checklist export and placeholder conversion.
- Added tests for conversion, normal-item rejection, checklist Markdown content, and UI wiring.

## Design notes

- No new database column was added.
- Placeholder detection is based on the deterministic placeholder title pattern created in v6.4.
- Conversion preserves the WorkItem ID, kind, project, and Requirement link.
- Checklist export reuses the existing release-risk dashboard logic so the UI and export stay consistent.

## Result

v6.5 turns risk hints into a practical review workflow: create placeholder, convert it into real work, export checklist, and review release readiness without adding dependencies.
