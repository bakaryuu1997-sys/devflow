async function loadV109RestoreConflictReport() {
  const data = await api("/api/release-governance/v10-9-restore-conflict-report?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.9 Restore Conflicts"));
}

async function loadV109GuardedRestorePlan() {
  const snapshot = await api("/api/release-governance/v10-6-rollback-snapshot?profile_id=core-risk");
  const data = await api("/api/release-governance/v10-9-guarded-restore-plan?profile_id=core-risk", { method: "POST", body: JSON.stringify(snapshot) });
  showRich("readiness", renderGenericGovernanceCard(data, "v10.9 Digest Lock Plan"));
}

async function executeV109GuardedManualRestore() {
  const snapshot = await api("/api/release-governance/v10-6-rollback-snapshot?profile_id=core-risk");
  const phrase = encodeURIComponent("RESTORE DEMO PROFILE: core-risk");
  const lock = encodeURIComponent(snapshot.snapshot_digest);
  const path = `/api/release-governance/v10-9-execute-guarded-manual-restore?profile_id=core-risk&restore_approval=${phrase}&snapshot_digest_lock=${lock}&operator_name=demo`;
  const data = await api(path, { method: "POST", body: JSON.stringify(snapshot) });
  showRich("readiness", renderGenericGovernanceCard(data, "v10.9 Locked Restore"));
}

async function loadV109RestoreDigestLockAuditTrail() {
  const data = await api("/api/release-governance/v10-9-restore-digest-lock-audit-trail?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.9 Digest Lock Audit"));
}

async function loadV109OperatorRestoreConflictPackage() {
  const data = await api("/api/release-governance/v10-9-operator-restore-conflict-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.9 Restore Package"));
}
