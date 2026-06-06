async function loadV120BaselineFreezeSummary() {
  const data = await api("/api/release-governance/v12-0-baseline-freeze-summary?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v12.0 Baseline Freeze"));
}

async function loadV120ProductionDeploymentChecklist() {
  const data = await api("/api/release-governance/v12-0-production-deployment-checklist?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v12.0 Deployment Checklist"));
}

async function loadV120OperatorDeploymentPackage() {
  const data = await api("/api/release-governance/v12-0-operator-deployment-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v12.0 Deployment Package"));
}
