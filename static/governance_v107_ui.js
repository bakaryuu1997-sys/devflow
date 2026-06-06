async function loadV107RollbackImportRehearsal() {
  const data = await api("/api/release-governance/v10-7-manual-rollback-import-rehearsal?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.7 Rollback Import Rehearsal"));
}

async function loadV107RestoreChecklist() {
  const data = await api("/api/release-governance/v10-7-restore-checklist?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.7 Restore Checklist"));
}

async function loadV107OperatorRestorePackage() {
  const data = await api("/api/release-governance/v10-7-operator-restore-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.7 Restore Package"));
}
