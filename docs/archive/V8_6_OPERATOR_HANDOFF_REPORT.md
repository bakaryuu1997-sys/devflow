# v8.6 Production Upgrade Runbook + Operator Handoff Report

## Goal

Turn the guarded v8.5 production migration workflow into operator-facing runbook and handoff artifacts.

## Delivered

- `GET /api/release-governance/production-upgrade-runbook`
- `GET /api/release-governance/operator-handoff-package`
- `scripts/export_upgrade_runbook.py`
- `scripts/operator_handoff_package.py`
- UI buttons: Upgrade Runbook and Operator Handoff

## Safety decision

v8.6 does not apply migration SQL. It exports instructions and handoff documents only. The v8.5 approval phrase remains mandatory for real database changes.
