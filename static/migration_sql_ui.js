async function loadDryRunSqlMigration() {
  const data = await api("/api/release-governance/dry-run-sql-migration");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderDryRunSqlMigration(data));
  toast("Dry-run SQL migration loaded.");
}

async function loadBackupChecklist() {
  const data = await api("/api/release-governance/backup-checklist");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderBackupChecklist(data));
  toast("Backup checklist loaded.");
}

function renderDryRunSqlMigration(data) {
  const state = data.status === "No SQL Needed" ? "pass" : "warn";
  return `<div class="readiness-card ${state}"><div><span class="readiness-label">DRY-RUN SQL MIGRATION</span>
    <h3>${escapeHtml(data.status)} · ${data.statement_count || 0} statements</h3>
    <p>Will apply changes: ${data.will_apply_changes ? "Yes" : "No"} · backup required: ${data.backup_required ? "Yes" : "No"}</p></div></div>
    ${renderSqlStatements(data.statements || [])}
    ${renderList("Apply order", data.apply_order || [])}
    ${renderList("Safety notes", data.safety_notes || [])}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadBackupChecklist()">Backup Checklist</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>
    ${debugBlock(data)}`;
}

function renderBackupChecklist(data) {
  return `<div class="readiness-card warn"><div><span class="readiness-label">BACKUP CHECKLIST</span>
    <h3>${escapeHtml(data.status)} · v${escapeHtml(data.version || "8.2")}</h3>
    <p>Target: ${escapeHtml(data.database_target || "devflow.db")}</p></div></div>
    ${renderChecklist("Backup steps", data.checklist || [])}
    ${renderChecklist("Verification", data.verification_steps || [])}
    ${renderChecklist("Rollback", data.rollback_steps || [])}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadDryRunSqlMigration()">Dry-run SQL</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>
    ${debugBlock(data)}`;
}

function renderSqlStatements(rows) {
  if (!rows.length) return renderList("SQL", ["No SQL needed for the current schema."]);
  return `<div class="result-list"><h4>SQL statements</h4>${rows.map(row => `
    <div class="result-card severity-Medium"><div class="result-head"><strong>${escapeHtml(row.target)}</strong><span class="safe-pill">${escapeHtml(row.kind)}</span></div>
    <pre>${escapeHtml(row.sql)}</pre><p>Destructive: ${row.destructive ? "Yes" : "No"}</p></div>`).join("")}</div>`;
}

function renderChecklist(title, rows) {
  if (!rows.length) return renderList(title, ["No checklist rows."]);
  return `<div class="result-list"><h4>${escapeHtml(title)}</h4>${rows.map(row => `<div class="result-card"><label><input type="checkbox" /> ${escapeHtml(row)}</label></div>`).join("")}</div>`;
}
