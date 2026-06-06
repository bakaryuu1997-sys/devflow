async function loadPreventionBurndownAnalytics() {
  const data = await api(`/api/projects/${projectId}/prevention-burndown-analytics`);
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderPreventionBurndownAnalytics(data));
  toast("Prevention burndown analytics loaded.");
}

async function loadOwnerWorkloadBalance() {
  const data = await api(`/api/projects/${projectId}/owner-workload-balance`);
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderOwnerWorkloadBalance(data));
  toast("Owner workload balance loaded.");
}

function renderPreventionBurndownAnalytics(data) {
  if (!data) return renderEmpty("No prevention burndown analytics available.");
  const cardState = data.overdue_items ? "fail" : (data.open_items ? "warn" : "pass");
  return `
    <div class="readiness-card ${cardState}"><div><span class="readiness-label">PREVENTION BURNDOWN</span>
      <h3>${escapeHtml(data.project_name)} · ${data.completion_rate || 0}% complete</h3>
      <p>Shows whether recurring-risk prevention work is burning down before the next release.</p></div></div>
    <div class="mini-grid review-summary">
      <span>Total <b>${data.total_items || 0}</b></span>
      <span>Open <b>${data.open_items || 0}</b></span>
      <span>Done <b>${data.done_items || 0}</b></span>
      <span>Overdue <b>${data.overdue_items || 0}</b></span>
      <span>Due soon <b>${data.due_soon_items || 0}</b></span>
    </div>
    ${renderList("Burndown hints", data.action_hints || [])}
    ${renderBurndownProjection(data.burndown_projection || [])}
    ${renderAtRiskPreventionItems(data.at_risk_items || [])}
    <div class="action-row compact-actions">
      <button type="button" class="ghost-btn" onclick="loadOwnerWorkloadBalance()">Owner workload balance</button>
      <button type="button" class="ghost-btn" onclick="loadPreventionExecutionBoard()">Execution board</button>
      <button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button>
    </div>
    ${debugBlock(data)}`;
}

function renderBurndownProjection(rows) {
  if (!rows.length) return renderList("Burndown projection", ["No projection data available."]);
  return `<div class="result-list"><h4>Burndown projection</h4>${rows.map(row => `
    <div class="result-card severity-${row.remaining_open_items ? "Medium" : "Low"}">
      <div class="result-head"><strong>${escapeHtml(row.checkpoint)}</strong><span class="safe-pill">${escapeHtml(row.date)}</span></div>
      <p>Remaining open: ${row.remaining_open_items} · Planned closed by checkpoint: ${row.planned_closed_by_checkpoint} · Missing due date: ${row.missing_due_date_items}</p>
    </div>`).join("")}</div>`;
}

function renderAtRiskPreventionItems(items) {
  if (!items.length) return renderList("At-risk prevention items", ["No overdue or due-soon prevention item right now."]);
  return `<div class="result-list"><h4>At-risk prevention items</h4>${items.map(item => `
    <div class="result-card severity-${item.is_overdue ? "High" : "Medium"}">
      <div class="result-head"><strong>#${item.id} ${escapeHtml(item.title)}</strong><span class="safe-pill">${escapeHtml(item.status)}</span></div>
      <p>Owner: ${escapeHtml(item.owner || "Unassigned")} · Due: ${escapeHtml(item.due_date || "No due date")}</p>
      <div class="action-row compact-actions">
        <button type="button" class="ghost-btn" onclick="updateReleaseLearningItemPlanning(${item.id})">Re-plan</button>
        <button type="button" class="ghost-btn" onclick="updateReleaseLearningItemStatus(${item.id}, 'Prevented')">Mark prevented</button>
      </div>
    </div>`).join("")}</div>`;
}

function renderOwnerWorkloadBalance(data) {
  if (!data) return renderEmpty("No owner workload balance data available.");
  const cardState = data.overloaded_owner_count || data.unassigned_open_items ? "warn" : "pass";
  return `
    <div class="readiness-card ${cardState}"><div><span class="readiness-label">OWNER WORKLOAD BALANCE</span>
      <h3>${escapeHtml(data.project_name)} · ${data.owner_count || 0} owner(s)</h3>
      <p>Highlights overloaded, unassigned, and due-soon prevention work before release planning slips.</p></div></div>
    <div class="mini-grid review-summary">
      <span>Avg open/owner <b>${data.average_open_items_per_owner || 0}</b></span>
      <span>Unassigned open <b>${data.unassigned_open_items || 0}</b></span>
      <span>Overloaded <b>${data.overloaded_owner_count || 0}</b></span>
    </div>
    ${renderList("Workload hints", data.action_hints || [])}
    ${renderOwnerWorkloadRows(data.owners || [])}
    <div class="action-row compact-actions">
      <button type="button" class="ghost-btn" onclick="loadPreventionBurndownAnalytics()">Prevention burndown</button>
      <button type="button" class="ghost-btn" onclick="loadNextReleaseReadiness()">Next release readiness</button>
      <button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button>
    </div>
    ${debugBlock(data)}`;
}

function renderOwnerWorkloadRows(rows) {
  if (!rows.length) return renderList("Owner workload", ["No prevention items yet."]);
  return `<div class="result-list"><h4>Owner workload</h4>${rows.map(row => `
    <div class="result-card severity-${row.status === "Overloaded" || row.status === "Needs Owner" ? "High" : (row.status === "Watch" ? "Medium" : "Low")}">
      <div class="result-head"><strong>${escapeHtml(row.owner)}</strong><span class="safe-pill">${escapeHtml(row.status)}</span></div>
      <p>Open: ${row.open_items} · Done: ${row.done_items} · Overdue: ${row.overdue_items} · Due soon: ${row.due_soon_items} · Escalated: ${row.escalated_items} · Score: ${row.workload_score}</p>
      ${renderOwnerOpenItems(row.items || [])}
    </div>`).join("")}</div>`;
}

function renderOwnerOpenItems(items) {
  if (!items.length) return "<p>No open items for this owner.</p>";
  return `<ul>${items.slice(0, 5).map(item => `<li>#${item.id} ${escapeHtml(item.title)} · ${escapeHtml(item.status)} · due ${escapeHtml(item.due_date || "No due date")}</li>`).join("")}</ul>`;
}
