async function loadV104SampleProjectBuilder() {
  const data = await api("/api/release-governance/v10-4-sample-project-builder?profile_id=core-risk");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.4 Sample Project Builder"));
}
async function buildV104SampleProject() {
  const data = await api("/api/release-governance/v10-4-build-sample-project?profile_id=core-risk&operator_name=local-operator", { method: "POST" });
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.4 Sample Project Built"));
}
async function loadV104TutorialCompletionBadge() {
  const data = await api("/api/release-governance/v10-4-tutorial-completion-badge");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.4 Completion Badge"));
}
async function loadV104OperatorSampleBuilderPackage() {
  const data = await api("/api/release-governance/v10-4-operator-sample-builder-package");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.4 Builder Package"));
}
