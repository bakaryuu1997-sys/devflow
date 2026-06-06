async function loadV119FinalReleaseTagPreparation() {
  const data = await api("/api/release-governance/v11-9-final-release-tag-preparation?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.9 Release Tag"));
}

async function loadV119PortfolioDemoScript() {
  const data = await api("/api/release-governance/v11-9-portfolio-demo-script?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.9 Portfolio Script"));
}

async function loadV119OperatorFinalReleasePackage() {
  const data = await api("/api/release-governance/v11-9-operator-final-release-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.9 Final Package"));
}
