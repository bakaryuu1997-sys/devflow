async function loadV101UsabilityWalkthrough() {
  const data = await api("/api/release-governance/v10-1-usability-walkthrough");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.1 Walkthrough"));
}
async function loadV101SampleDemoScript() {
  const data = await api("/api/release-governance/v10-1-sample-demo-script");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.1 Demo Script"));
}
async function loadV101OptionalDeploymentGuide() {
  const data = await api("/api/release-governance/v10-1-optional-deployment-guide");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.1 Deployment Guide"));
}
async function loadV101OperatorQuickstartPackage() {
  const data = await api("/api/release-governance/v10-1-operator-quickstart-package");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.1 Operator Quickstart"));
}
