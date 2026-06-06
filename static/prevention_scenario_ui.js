async function loadReleaseReadinessScenarios() {
  const targetDays = prompt("Target planning window in days", "14") || "14";
  const data = await api(`/api/projects/${projectId}/release-readiness-scenarios?target_days=${encodeURIComponent(targetDays)}`);
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderReleaseReadinessScenarios(data));
  toast("Release readiness scenarios loaded.");
}

async function adjustPreventionScope(itemId, statusValue) {
  const reason = prompt("Why adjust this prevention item scope?", "Scope decision for next release planning") || "";
  const payload = { status: statusValue, reason };
  const data = await api(`/api/release-learning-items/${itemId}/scope-adjustment`, {
    method: "POST", body: JSON.stringify(payload),
  });
  if (data.content) window.lastEvidenceMarkdown = data.content;
  toast(data.message || "Prevention scope adjusted.");
  await loadReleaseReadinessScenarios();
}

function renderReleaseReadinessScenarios(data) {
  if (!data) return renderEmpty("No scenario planning data available.");
  const baseline = (data.scenarios || [])[0] || {};
  const state = baseline.status === "At Risk" ? "fail" : (baseline.status === "Ready Candidate" ? "pass" : "warn");
  return `
    <div class="readiness-card ${state}"><div><span class="readiness-label">SCENARIO PLANNING</span>
      <h3>${escapeHtml(data.project_name)} · ${escapeHtml(baseline.status || "Unknown")}</h3>
      <p>Compare prevention scope choices before committing to the next release plan.</p></div></div>
    <div class="mini-grid review-summary">
      <span>Active scope <b>${data.active_scope_items || 0}</b></span>
      <span>Scoped out <b>${data.scoped_out_items || 0}</b></span>
      <span>Target window <b>${data.target_days || 14}d</b></span>
    </div>
    ${renderList("Scenario hints", data.action_hints || [])}
    ${renderScenarioRows(data.scenarios || [])}
    <div class="action-row compact-actions">
      <button type="button" class="ghost-btn" onclick="loadReleaseReadinessTimeline()">Readiness timeline</button>
      <button type="button" class="ghost-btn" onclick="loadPreventionCalendarView()">Prevention calendar</button>
      <button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button>
    </div>
    ${debugBlock(data)}`;
}

function renderScenarioRows(rows) {
  if (!rows.length) return renderList("Scenarios", ["No scenarios available."]);
  return `<div class="result-list"><h4>Readiness scenarios</h4>${rows.map(row => `
    <div class="result-card severity-${row.status === "At Risk" ? "High" : (row.status === "Ready Candidate" ? "Low" : "Medium")}">
      <div class="result-head"><strong>${escapeHtml(row.name)}</strong><span class="safe-pill">${escapeHtml(row.status)}</span></div>
      <p>${escapeHtml(row.note || "")}</p>
      <p>Score: ${row.readiness_score} · Active: ${row.active_scope_items} · Overdue: ${row.overdue_items} · Unscheduled: ${row.unscheduled_items} · Scope adjustment: ${row.scope_adjustment}</p>
      ${renderScenarioScopeItems(row.items_out_by_scenario || [])}
    </div>`).join("")}</div>`;
}

function renderScenarioScopeItems(items) {
  if (!items.length) return "";
  return `<div class="small-card"><strong>Items changed by this scenario</strong>${items.map(item => `
    <p>#${item.id} ${escapeHtml(item.title)} · ${escapeHtml(item.status)} · due ${escapeHtml(item.due_date || "No due date")}</p>
    <div class="action-row compact-actions">
      <button type="button" class="ghost-btn" onclick="adjustPreventionScope(${item.id}, 'Deferred')">Defer</button>
      <button type="button" class="ghost-btn" onclick="adjustPreventionScope(${item.id}, 'Out of Scope')">Out of scope</button>
      <button type="button" class="ghost-btn" onclick="adjustPreventionScope(${item.id}, 'Open')">Keep in scope</button>
    </div>`).join("")}</div>`;
}
