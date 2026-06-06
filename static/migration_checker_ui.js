async function loadLocalMigrationCheck() {
  const data = await api("/api/release-governance/local-migration-check");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderLocalMigrationCheck(data));
  toast("Local migration check loaded.");
}

async function loadUpgradeSafetyReport() {
  const data = await api("/api/release-governance/upgrade-safety-report");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderUpgradeSafetyReport(data));
  toast("Upgrade safety report loaded.");
}

function renderLocalMigrationCheck(data) {
  const state = data.status === "Ready" ? "pass" : (data.status === "Migration Needed" ? "warn" : "fail");
  return `<div class="readiness-card ${state}"><div><span class="readiness-label">LOCAL MIGRATION CHECK</span>
    <h3>${escapeHtml(data.status)} · v${escapeHtml(data.version || "8.1")}</h3>
    <p>Safe to upgrade: ${data.safe_to_upgrade ? "Yes" : "No"} · missing columns: ${data.missing_column_count || 0}</p></div></div>
    ${renderMigrationSchemaRows(data.required_schema || [])}
    ${renderList("Upgrade steps", data.upgrade_steps || [])}
    ${renderList("Action hints", data.action_hints || [])}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadUpgradeSafetyReport()">Upgrade Safety Report</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>
    ${debugBlock(data)}`;
}

function renderUpgradeSafetyReport(data) {
  const state = data.status === "Upgrade Safe" ? "pass" : (data.risk_score >= 70 ? "fail" : "warn");
  return `<div class="readiness-card ${state}"><div><span class="readiness-label">UPGRADE SAFETY</span>
    <h3>${escapeHtml(data.status)} · ${data.risk_score}/100</h3>
    <p>Migration check: ${escapeHtml(data.migration_check_status)} · backup required: ${data.backup_required ? "Yes" : "No"}</p></div></div>
    ${renderList("Must fix before upgrade", data.must_fix_before_upgrade || ["No required fixes."])}
    ${renderList("Recommended order", data.recommended_order || [])}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadLocalMigrationCheck()">Local Migration Check</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>
    ${debugBlock(data)}`;
}

function renderMigrationSchemaRows(rows) {
  if (!rows.length) return renderList("Required schema", ["No schema checks available."]);
  return `<div class="result-list"><h4>Required schema</h4>${rows.map(row => `
    <div class="result-card severity-${row.state === "PASS" ? "Low" : "High"}">
      <div class="result-head"><strong>${escapeHtml(row.table)}</strong><span class="safe-pill">${escapeHtml(row.state)}</span></div>
      <p>Missing: ${escapeHtml((row.missing_columns || []).join(", ") || "none")}</p>
    </div>`).join("")}</div>`;
}
