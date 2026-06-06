async function loadVerifiedEvidenceManifestGate() {
  const data = await api("/api/release-governance/verified-evidence-manifest-gate");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "Verified Evidence Manifest Gate"));
  toast("Verified evidence gate loaded.");
}
async function loadExternalVerifierProfiles() {
  const data = await api("/api/release-governance/external-verifier-profiles");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "External Verifier Profiles"));
}
async function createDefaultVerifierProfile() {
  const data = await api("/api/release-governance/external-verifier-profiles", { method: "POST", body: JSON.stringify({ name: "ops-ed25519", key_reference: "external-public-key" }) });
  showRich("readiness", debugBlock(data));
}
async function loadOperatorPolicyPresets() {
  const data = await api("/api/release-governance/operator-policy-presets");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "Operator Policy Presets"));
}
async function loadFinalSignedEvidenceBundle() {
  const data = await api("/api/release-governance/final-signed-evidence-bundle");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "Final Signed Evidence Bundle"));
}
async function createFinalSignedEvidenceBundle() {
  const data = await api("/api/release-governance/final-signed-evidence-bundles", { method: "POST", body: JSON.stringify({}) });
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "Final Bundle Record"));
}
async function loadEndToEndGovernanceRehearsal() {
  const data = await api("/api/release-governance/end-to-end-governance-rehearsal");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "End-to-End Rehearsal"));
}
async function loadV10StableMilestoneReport() {
  const data = await api("/api/release-governance/v10-stable-milestone-report");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "Stable Milestone"));
}
async function loadV10InstallerChecklist() {
  const data = await api("/api/release-governance/v10-installer-checklist");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "Installer Checklist"));
}
function renderGenericGovernanceCard(data, title) {
  const status = data.status || data.mode || title;
  const ready = data.ready === undefined ? true : data.ready;
  return `<div class="readiness-card ${ready ? "success" : "danger"}"><div><span class="readiness-label">${escapeHtml(title)}</span><h3>${escapeHtml(status)}</h3><p>version=${escapeHtml(data.version || "")}</p></div></div>${renderList("Blockers", data.blockers || ["No blockers."])}<div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button><button type="button" class="ghost-btn" onclick="createDefaultVerifierProfile()">Create verifier profile</button><button type="button" class="ghost-btn" onclick="createFinalSignedEvidenceBundle()">Create final bundle</button></div>${debugBlock(data)}`;
}
