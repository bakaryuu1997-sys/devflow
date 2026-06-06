async function loadV108GuardedRestorePlan() {
  const data = await api("/api/release-governance/v10-8-guarded-restore-plan?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.8 Guarded Restore Plan"));
}

async function executeV108GuardedManualRestore() {
  const phrase = encodeURIComponent("RESTORE DEMO PROFILE: core-risk");
  const data = await api(`/api/release-governance/v10-8-execute-guarded-manual-restore?profile_id=core-risk&restore_approval=${phrase}&operator_name=demo`, { method: "POST" });
  showRich("readiness", renderGenericGovernanceCard(data, "v10.8 Manual Restore"));
}

async function loadV108RestoreAuditTrail() {
  const data = await api("/api/release-governance/v10-8-restore-audit-trail?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.8 Restore Audit"));
}

async function loadV108OperatorRestoreExecutionPackage() {
  const data = await api("/api/release-governance/v10-8-operator-restore-execution-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.8 Restore Package"));
}
