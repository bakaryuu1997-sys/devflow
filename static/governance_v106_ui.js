async function loadV106RollbackSnapshot() {
  const data = await api("/api/release-governance/v10-6-rollback-snapshot?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.6 Rollback Snapshot"));
}

async function executeV106ProfileReset() {
  const phrase = "RESET DEMO PROFILE: core-risk";
  const url = `/api/release-governance/v10-6-execute-profile-reset?profile_id=core-risk&approval=${encodeURIComponent(phrase)}&operator_name=local-operator`;
  const data = await api(url, { method: "POST" });
  showRich("readiness", renderGenericGovernanceCard(data, "v10.6 Reset With Audit"));
}

async function loadV106ProfileResetAuditTrail() {
  const data = await api("/api/release-governance/v10-6-profile-reset-audit-trail?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.6 Reset Audit Trail"));
}

async function loadV106OperatorRollbackPackage() {
  const data = await api("/api/release-governance/v10-6-operator-rollback-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.6 Rollback Package"));
}
