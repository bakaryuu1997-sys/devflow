async function loadProductionUpgradeRunbook() {
  const data = await api("/api/release-governance/production-upgrade-runbook");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderProductionUpgradeRunbook(data));
  toast("Production upgrade runbook loaded.");
}

async function loadOperatorHandoffPackage() {
  const data = await api("/api/release-governance/operator-handoff-package");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderOperatorHandoffPackage(data));
  toast("Operator handoff package loaded.");
}

function renderProductionUpgradeRunbook(data) {
  const state = data.status === "Blocked" ? "danger" : "warn";
  return `<div class="readiness-card ${state}"><div><span class="readiness-label">PRODUCTION UPGRADE RUNBOOK</span>
    <h3>${escapeHtml(data.status)}</h3><p>Database: ${escapeHtml(data.source_database || "unknown")} · approval: ${escapeHtml(data.approval_phrase || "")}</p></div></div>
    ${renderList("Go / No-Go", [data.go_no_go || "No decision available."])}
    ${(data.phases || []).map(phase => renderChecklist(phase.name, phase.items || [])).join("")}
    ${renderChecklist("Operator commands", data.operator_commands || [])}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadOperatorHandoffPackage()">Operator handoff</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>
    ${debugBlock(data)}`;
}

function renderOperatorHandoffPackage(data) {
  return `<div class="readiness-card warn"><div><span class="readiness-label">OPERATOR HANDOFF PACKAGE</span>
    <h3>${escapeHtml(data.status)}</h3><p>Package: ${escapeHtml(data.package_name || "")}</p></div></div>
    ${renderHandoffManifest(data.manifest || {})}
    ${renderChecklist("Required files", data.required_files || [])}
    ${(data.handoff_sections || []).map(section => renderChecklist(section.name, section.items || [])).join("")}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadProductionUpgradeRunbook()">Runbook</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>
    ${debugBlock(data)}`;
}

function renderHandoffManifest(manifest) {
  const rows = Object.keys(manifest).map(key => `<div class="result-card"><strong>${escapeHtml(key)}</strong><p>${escapeHtml(String(manifest[key]))}</p></div>`).join("");
  return `<div class="result-list"><h4>Manifest</h4>${rows || "<p>No manifest available.</p>"}</div>`;
}
