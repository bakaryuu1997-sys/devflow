async function loadReleaseGovernanceReadiness() {
  const targetDays = prompt("Target governance planning window in days", "14") || "14";
  const data = await api(`/api/projects/${projectId}/release-governance-readiness?target_days=${encodeURIComponent(targetDays)}`);
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderReleaseGovernanceReadiness(data));
  toast("Release governance readiness loaded.");
}

async function loadMigrationNotes() {
  const data = await api("/api/release-governance/migration-notes");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderMigrationNotes(data));
  toast("Migration notes loaded.");
}

function renderReleaseGovernanceReadiness(data) {
  const state = data.status === "Audit Ready" ? "pass" : (data.score >= 70 ? "warn" : "fail");
  const plan = data.recommended_plan || {};
  return `
    <div class="readiness-card ${state}"><div><span class="readiness-label">GOVERNANCE MILESTONE</span>
      <h3>${escapeHtml(data.status)} · ${data.score}/100</h3>
      <p>Recommended plan: ${escapeHtml(plan.name || "None")} · sign-offs: ${data.signoff_count || 0} · scope audits: ${data.scope_audit_count || 0}</p></div></div>
    <div class="mini-grid review-summary">
      <span>Ready for sign-off <b>${data.ready_for_signoff ? "Yes" : "No"}</b></span>
      <span>Expected gain <b>${data.expected_score_gain || 0}</b></span>
      <span>Target <b>${data.target_days || 14}d</b></span>
    </div>
    ${renderGovernanceChecks(data.checks || [])}
    ${renderList("Governance action hints", data.action_hints || [])}
    ${renderMigrationRows(data.migration_notes || [])}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadReleasePlanRecommendation()">Plan Recommendation</button><button type="button" class="ghost-btn" onclick="loadScopeDecisionAudit()">Scope Audit</button><button type="button" class="ghost-btn" onclick="loadMigrationNotes()">Migration Notes</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>
    ${debugBlock(data)}`;
}

function renderGovernanceChecks(rows) {
  if (!rows.length) return renderList("Governance checks", ["No governance checks available."]);
  return `<div class="result-list"><h4>Governance checks</h4>${rows.map(row => `
    <div class="result-card severity-${row.passed ? "Low" : "High"}">
      <div class="result-head"><strong>${escapeHtml(row.name)}</strong><span class="safe-pill">${escapeHtml(row.state)}</span></div>
      <p>${escapeHtml(row.detail || "")}</p>
    </div>`).join("")}</div>`;
}

function renderMigrationRows(rows) {
  if (!rows.length) return renderList("Migration notes", ["No migration notes available."]);
  return `<div class="result-list"><h4>Migration notes</h4>${rows.map(row => `
    <div class="result-card"><div class="result-head"><strong>${escapeHtml(row.area)}</strong><span class="safe-pill">v8.0</span></div><p>${escapeHtml(row.action)}</p></div>`).join("")}</div>`;
}

function renderMigrationNotes(data) {
  return `<div class="readiness-card warn"><div><span class="readiness-label">MIGRATION NOTES</span><h3>v${escapeHtml(data.version || "8.0")}</h3><p>Database upgrade notes for non-demo SQLite usage.</p></div></div>
    ${renderMigrationRows(data.notes || [])}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>${debugBlock(data)}`;
}
