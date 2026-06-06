async function loadProductionUpgradeRehearsalReport() {
  const data = await api("/api/release-governance/production-upgrade-rehearsal-report");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderProductionUpgradeRehearsalReport(data));
  toast("Production rehearsal report loaded.");
}

async function loadOperatorSignoffChecklist() {
  const data = await api("/api/release-governance/operator-signoff-checklist");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderOperatorSignoffChecklist(data));
  toast("Operator sign-off checklist loaded.");
}

function renderProductionUpgradeRehearsalReport(data) {
  const state = data.status === "Rehearsal Blocked" ? "danger" : "warn";
  return `<div class="readiness-card ${state}"><div><span class="readiness-label">PRODUCTION REHEARSAL</span>
    <h3>${escapeHtml(data.status)}</h3><p>Score: ${escapeHtml(String(data.rehearsal_score || 0))} · ${escapeHtml(data.go_no_go || "")}</p></div></div>
    ${renderRehearsalEvidence(data.evidence || [])}
    ${(data.rehearsal_steps || []).map(step => renderChecklist(step.name, step.items || [])).join("")}
    ${renderList("Operator findings", data.operator_findings || [])}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadOperatorSignoffChecklist()">Operator sign-off</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>
    ${debugBlock(data)}`;
}

function renderOperatorSignoffChecklist(data) {
  return `<div class="readiness-card warn"><div><span class="readiness-label">OPERATOR SIGN-OFF</span>
    <h3>${escapeHtml(data.status)}</h3><p>Approval phrase: ${escapeHtml(data.approval_phrase || "")}</p></div></div>
    ${renderSignoffRows(data.required_signoffs || [])}
    ${renderChecklist("Operator attestations", data.operator_attestations || [])}
    ${data.blocked_until && data.blocked_until.length ? renderList("Blocked until", data.blocked_until) : ""}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadProductionUpgradeRehearsalReport()">Rehearsal report</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>
    ${debugBlock(data)}`;
}

function renderRehearsalEvidence(rows) {
  const cards = rows.map(row => `<div class="result-card"><strong>${escapeHtml(row.name)}</strong><p>${escapeHtml(row.status)}</p></div>`).join("");
  return `<div class="result-list"><h4>Rehearsal evidence</h4>${cards || "<p>No evidence.</p>"}</div>`;
}

function renderSignoffRows(rows) {
  const cards = rows.map(row => `<div class="result-card"><strong>${escapeHtml(row.role)}</strong><p>${escapeHtml(row.item)}</p></div>`).join("");
  return `<div class="result-list"><h4>Required sign-offs</h4>${cards || "<p>No sign-offs.</p>"}</div>`;
}
