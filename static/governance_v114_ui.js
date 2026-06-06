async function loadV114RecoveryEvidenceBundle() {
  const data = await api("/api/release-governance/v11-4-recovery-evidence-bundle?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.4 Recovery Evidence Bundle"));
}

async function loadV114FinalDemoHandoffPolish() {
  const data = await api("/api/release-governance/v11-4-final-demo-handoff-polish?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.4 Final Demo Handoff"));
}

async function loadV114OperatorDemoHandoffPackage() {
  const data = await api("/api/release-governance/v11-4-operator-demo-handoff-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.4 Demo Handoff Package"));
}
