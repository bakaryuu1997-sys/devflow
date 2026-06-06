async function loadV115DemoReleaseCandidateFreeze() {
  const data = await api("/api/release-governance/v11-5-demo-release-candidate-freeze?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.5 Demo RC Freeze"));
}

async function loadV115OperatorAcceptanceChecklist() {
  const data = await api("/api/release-governance/v11-5-operator-acceptance-checklist?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.5 Acceptance Checklist"));
}

async function loadV115OperatorReleaseCandidatePackage() {
  const data = await api("/api/release-governance/v11-5-operator-release-candidate-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.5 RC Package"));
}
