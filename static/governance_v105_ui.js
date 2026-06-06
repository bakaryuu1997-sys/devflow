async function loadV105ProfileResetPlan() {
  const data = await api("/api/release-governance/v10-5-profile-reset-plan?profile_id=core-risk");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.5 Profile Reset Plan"));
}
async function executeV105ProfileReset() {
  const phrase = "RESET DEMO PROFILE: core-risk";
  const data = await api(`/api/release-governance/v10-5-execute-profile-reset?profile_id=core-risk&approval=${encodeURIComponent(phrase)}&operator_name=local-operator`, { method: "POST" });
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.5 Profile Reset Complete"));
}
async function loadV105OperatorResetPackage() {
  const data = await api("/api/release-governance/v10-5-operator-reset-package?profile_id=core-risk");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.5 Reset Package"));
}
