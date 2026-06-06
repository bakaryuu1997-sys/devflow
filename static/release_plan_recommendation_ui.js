async function loadReleasePlanRecommendation() {
  const targetDays = prompt("Target planning window in days", "14") || "14";
  const data = await api(`/api/projects/${projectId}/release-plan-recommendation?target_days=${encodeURIComponent(targetDays)}`);
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderReleasePlanRecommendation(data));
  toast("Release plan recommendation loaded.");
}

async function loadScopeDecisionAudit() {
  const data = await api(`/api/projects/${projectId}/scope-decision-audit`);
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderScopeDecisionAudit(data));
  toast("Scope decision audit loaded.");
}

function renderReleasePlanRecommendation(data) {
  const plan = data.recommended_plan || {};
  const state = plan.status === "At Risk" ? "fail" : (plan.status === "Ready Candidate" ? "pass" : "warn");
  return `
    <div class="readiness-card ${state}"><div><span class="readiness-label">PLAN RECOMMENDATION</span>
      <h3>${escapeHtml(plan.name || "No plan")} · ${escapeHtml(plan.status || "Unknown")}</h3>
      <p>Baseline ${data.baseline_score}/100 → recommended ${plan.readiness_score || 0}/100. Gain: ${data.expected_score_gain || 0}.</p></div></div>
    <div class="mini-grid review-summary">
      <span>Target <b>${data.target_days || 14}d</b></span><span>Audit records <b>${data.decision_audit_count || 0}</b></span>
      <span>Scope adjustment <b>${plan.scope_adjustment || 0}</b></span>
    </div>
    ${renderList("Recommendation hints", data.action_hints || [])}
    ${renderPlanScenarioRows(data.ranked_scenarios || [])}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadScopeDecisionAudit()">Scope decision audit</button><button type="button" class="ghost-btn" onclick="loadReleaseReadinessScenarios()">Scenario planning</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>
    ${debugBlock(data)}`;
}

function renderPlanScenarioRows(rows) {
  if (!rows.length) return renderList("Ranked scenarios", ["No scenarios available."]);
  return `<div class="result-list"><h4>Ranked release plans</h4>${rows.map(row => `
    <div class="result-card severity-${row.status === "At Risk" ? "High" : (row.status === "Ready Candidate" ? "Low" : "Medium")}">
      <div class="result-head"><strong>${escapeHtml(row.name)}</strong><span class="safe-pill">${escapeHtml(row.status)}</span></div>
      <p>Score: ${row.readiness_score} · Active: ${row.active_scope_items} · Overdue: ${row.overdue_items} · Unscheduled: ${row.unscheduled_items} · Scope adjustment: ${row.scope_adjustment}</p>
    </div>`).join("")}</div>`;
}

function renderScopeDecisionAudit(data) {
  const rows = data.decisions || [];
  return `<div class="readiness-card warn"><div><span class="readiness-label">SCOPE AUDIT</span><h3>${escapeHtml(data.project_name)} · ${rows.length} decision(s)</h3><p>Audit trail for prevention scope changes.</p></div></div>
    ${rows.length ? `<div class="result-list"><h4>Scope decisions</h4>${rows.map(row => `<div class="result-card"><div class="result-head"><strong>#${row.id} ${escapeHtml(row.item_title)}</strong><span class="safe-pill">${escapeHtml(row.old_status)} → ${escapeHtml(row.new_status)}</span></div><p>${escapeHtml(row.reason || "No reason")}</p><small>${escapeHtml(row.created_at || "")}</small></div>`).join("")}</div>` : renderList("Scope decisions", ["No scope decisions recorded yet."])}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>${debugBlock(data)}`;
}
