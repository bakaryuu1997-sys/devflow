async function loadV103DemoDataProfiles() {
  const data = await api("/api/release-governance/v10-3-demo-data-profiles");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.3 Demo Data Profiles"));
}
async function loadV103DemoProfileResetPlan() {
  const data = await api("/api/release-governance/v10-3-demo-profile-reset-plan?profile_id=core-risk");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.3 Demo Profile Reset Plan"));
}
async function loadV103TutorialProgress() {
  const data = await api("/api/release-governance/v10-3-tutorial-progress");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.3 Tutorial Progress"));
}
async function completeV103TutorialStep() {
  const data = await api("/api/release-governance/v10-3-tutorial-progress/profile?status=Done&operator_name=local-operator", { method: "POST" });
  showRich("readiness", renderGenericGovernanceCard(data, "v10.3 Tutorial Step Saved"));
}
async function loadV103OperatorTutorialPackage() {
  const data = await api("/api/release-governance/v10-3-operator-tutorial-package");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.3 Operator Tutorial Package"));
}
