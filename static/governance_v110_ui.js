async function loadV110RestoreGovernanceStabilityReport() {
  const snapshot = await api("/api/release-governance/v10-6-rollback-snapshot?profile_id=core-risk");
  const data = await api("/api/release-governance/v11-0-restore-governance-stability-report?profile_id=core-risk", { method: "POST", body: JSON.stringify(snapshot) });
  showRich("readiness", renderGenericGovernanceCard(data, "v11.0 Recovery Stability"));
}

async function loadV110FinalOperatorRecoveryRunbook() {
  const snapshot = await api("/api/release-governance/v10-6-rollback-snapshot?profile_id=core-risk");
  const data = await api("/api/release-governance/v11-0-final-operator-recovery-runbook?profile_id=core-risk", { method: "POST", body: JSON.stringify(snapshot) });
  showRich("readiness", renderGenericGovernanceCard(data, "v11.0 Recovery Runbook"));
}

async function loadV110OperatorRecoveryPackage() {
  const data = await api("/api/release-governance/v11-0-operator-recovery-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.0 Recovery Package"));
}
