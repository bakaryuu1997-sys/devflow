async function loadManualMigrationApplyAssistant() {
  const data = await api("/api/release-governance/manual-migration-apply-assistant");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderManualMigrationApplyAssistant(data));
  toast("Manual migration apply assistant loaded.");
}

async function loadPostMigrationVerificationSnapshot() {
  const data = await api("/api/release-governance/post-migration-verification-snapshot");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderPostMigrationVerificationSnapshot(data));
  toast("Post-migration verification snapshot loaded.");
}

function renderManualMigrationApplyAssistant(data) {
  const state = data.status === "Already Migrated" ? "pass" : "warn";
  return `<div class="readiness-card ${state}"><div><span class="readiness-label">MANUAL MIGRATION APPLY ASSISTANT</span>
    <h3>${escapeHtml(data.status)} · ${data.statement_count || 0} statements</h3>
    <p>Will apply changes: ${data.will_apply_changes ? "Yes" : "No"} · backup required: ${data.backup_required ? "Yes" : "No"}</p></div></div>
    ${renderApplyPreflight(data.preflight_checks || [])}
    ${renderChecklist("Manual apply steps", data.manual_apply_steps || [])}
    <div class="result-list"><h4>SQL script</h4><div class="result-card"><pre>${escapeHtml(data.sql_script || "")}</pre></div></div>
    ${renderChecklist("Post-apply verification", data.post_apply_verification || [])}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadPostMigrationVerificationSnapshot()">Post-migration verify</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>
    ${debugBlock(data)}`;
}

function renderPostMigrationVerificationSnapshot(data) {
  const state = data.status === "Verified" ? "pass" : "warn";
  return `<div class="readiness-card ${state}"><div><span class="readiness-label">POST-MIGRATION VERIFICATION</span>
    <h3>${escapeHtml(data.status)} · remaining SQL ${data.remaining_sql_count || 0}</h3>
    <p>Schema ready: ${data.schema_ready ? "Yes" : "No"} · safe to upgrade: ${data.safe_to_upgrade ? "Yes" : "No"}</p></div></div>
    ${renderVerifiedSchema(data.verified_schema || [])}
    ${renderList("Remaining actions", data.remaining_actions || [])}
    ${renderList("Recommended next steps", data.recommended_next_steps || [])}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadManualMigrationApplyAssistant()">Apply Assistant</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>
    ${debugBlock(data)}`;
}

function renderApplyPreflight(rows) {
  if (!rows.length) return renderList("Preflight", ["No preflight checks found."]);
  return `<div class="result-list"><h4>Preflight checks</h4>${rows.map(row => `<div class="result-card"><strong>${escapeHtml(row.name)}</strong><p>${escapeHtml(row.status)}</p></div>`).join("")}</div>`;
}

function renderVerifiedSchema(rows) {
  if (!rows.length) return renderList("Verified schema", ["No schema rows found."]);
  return `<div class="result-list"><h4>Verified schema</h4>${rows.map(row => `<div class="result-card"><strong>${escapeHtml(row.table)}</strong><p>${escapeHtml(row.state)} · missing: ${escapeHtml((row.missing_columns || []).join(", ") || "none")}</p></div>`).join("")}</div>`;
}

async function loadSafeCopyMigrationApply() {
  const data = await api("/api/release-governance/safe-copy-migration-apply");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderSafeCopyMigrationApply(data));
  toast("Safe copy migration apply assistant loaded.");
}

async function loadRollbackDrillAutomation() {
  const data = await api("/api/release-governance/rollback-drill-automation");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderRollbackDrillAutomation(data));
  toast("Rollback drill automation loaded.");
}

function renderSafeCopyMigrationApply(data) {
  const state = data.status === "No Copy Apply Needed" ? "pass" : "warn";
  return `<div class="readiness-card ${state}"><div><span class="readiness-label">SAFE COPY MIGRATION APPLY</span>
    <h3>${escapeHtml(data.status)} · ${data.statement_count || 0} statements</h3>
    <p>Original DB modified: ${data.will_modify_original_database ? "Yes" : "No"} · copy DB: ${escapeHtml(data.recommended_copy_database || "")}</p></div></div>
    ${renderApplyPreflight(data.preflight_checks || [])}
    ${renderChecklist("Copy apply steps", data.copy_apply_steps || [])}
    ${renderChecklist("Commands", data.commands || [])}
    <div class="result-list"><h4>SQL script</h4><div class="result-card"><pre>${escapeHtml(data.sql_script || "")}</pre></div></div>
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadRollbackDrillAutomation()">Rollback drill</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>
    ${debugBlock(data)}`;
}

function renderRollbackDrillAutomation(data) {
  const state = data.status === "Rollback Drill Ready" ? "warn" : "danger";
  return `<div class="readiness-card ${state}"><div><span class="readiness-label">ROLLBACK DRILL AUTOMATION</span>
    <h3>${escapeHtml(data.status)}</h3>
    <p>Original DB modified: ${data.will_modify_original_database ? "Yes" : "No"} · source: ${escapeHtml(data.source_database || "")}</p></div></div>
    ${renderChecklist("Drill steps", data.drill_steps || [])}
    ${renderChecklist("Commands", data.commands || [])}
    ${renderList("Success criteria", data.success_criteria || [])}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadSafeCopyMigrationApply()">Safe copy apply</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>
    ${debugBlock(data)}`;
}


async function loadHumanApprovedRealMigrationGate() {
  const data = await api("/api/release-governance/human-approved-real-migration-gate");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderHumanApprovedRealMigrationGate(data));
  toast("Human-approved real migration gate loaded.");
}

async function loadFinalProductionUpgradeChecklist() {
  const data = await api("/api/release-governance/final-production-upgrade-checklist");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderFinalProductionUpgradeChecklist(data));
  toast("Final production upgrade checklist loaded.");
}

function renderHumanApprovedRealMigrationGate(data) {
  const state = data.status === "Blocked" ? "danger" : "warn";
  return `<div class="readiness-card ${state}"><div><span class="readiness-label">REAL MIGRATION GATE</span>
    <h3>${escapeHtml(data.status)} · ${data.statement_count || 0} statements</h3>
    <p>Original DB modified by final command: ${data.will_modify_original_database ? "Yes" : "No"} · approval: ${escapeHtml(data.approval_phrase || "")}</p></div></div>
    ${renderList("Blockers", data.blockers || ["No automatic blockers detected."])}
    ${renderChecklist("Required evidence", data.required_evidence || [])}
    ${renderChecklist("Approval commands", data.approval_commands || [])}
    ${renderChecklist("Rollback commands", data.rollback_commands || [])}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadFinalProductionUpgradeChecklist()">Production checklist</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>
    ${debugBlock(data)}`;
}

function renderFinalProductionUpgradeChecklist(data) {
  return `<div class="readiness-card warn"><div><span class="readiness-label">PRODUCTION UPGRADE CHECKLIST</span>
    <h3>${escapeHtml(data.status)}</h3><p>${escapeHtml(data.final_go_no_go || "")}</p></div></div>
    ${(data.sections || []).map(section => renderChecklist(section.name, section.items || [])).join("")}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadHumanApprovedRealMigrationGate()">Real migration gate</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>
    ${debugBlock(data)}`;
}
