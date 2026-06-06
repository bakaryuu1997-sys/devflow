async function loadV102FirstRunWizard() {
  const data = await api("/api/release-governance/v10-2-first-run-wizard");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.2 First-run Wizard"));
}
async function loadV102DemoResetSafetyCheck() {
  const data = await api("/api/release-governance/v10-2-demo-reset-safety-check");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.2 Demo Reset Safety"));
}
async function loadV102DemoResetPlan() {
  const data = await api("/api/release-governance/v10-2-demo-reset-plan");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.2 Demo Reset Plan"));
}
async function loadV102OperatorFirstRunPackage() {
  const data = await api("/api/release-governance/v10-2-operator-first-run-package");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.2 Operator First-run Package"));
}
