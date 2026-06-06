async function loadPreventionExecutionBoard() {
  const data = await api(`/api/projects/${projectId}/prevention-execution-board`);
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderPreventionExecutionBoard(data));
  toast("Prevention execution board loaded.");
}

async function loadOverdueRiskEscalations() {
  const data = await api(`/api/projects/${projectId}/overdue-risk-escalations`);
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderOverdueRiskEscalations(data));
  toast("Overdue risk escalations loaded.");
}

async function escalateReleaseLearningItem(itemId) {
  const reason = prompt("Escalation reason", "Overdue prevention item needs release-owner attention before next release.") || "";
  const data = await api(`/api/release-learning-items/${itemId}/escalate`, {
    method: "POST",
    body: JSON.stringify({ reason })
  });
  toast(data.message || "Prevention item escalated.");
  await loadPreventionExecutionBoard();
}

function renderPreventionExecutionBoard(data) {
  if (!data) return renderEmpty("No prevention execution board data available.");
  const boardState = data.overdue_items || data.escalated_items ? "fail" : (data.open_items ? "warn" : "pass");
  return `
    <div class="readiness-card ${boardState}"><div><span class="readiness-label">PREVENTION EXECUTION BOARD</span>
      <h3>${escapeHtml(data.project_name)} · ${data.open_items || 0} open item(s)</h3>
      <p>Tracks prevention work by execution lane and highlights overdue recurring-risk controls.</p></div></div>
    <div class="mini-grid review-summary">
      <span>Planned <b>${data.planned_items || 0}</b></span>
      <span>Due soon <b>${data.due_soon_items || 0}</b></span>
      <span>Overdue <b>${data.overdue_items || 0}</b></span>
      <span>Escalated <b>${data.escalated_items || 0}</b></span>
      <span>Done <b>${data.done_items || 0}</b></span>
    </div>
    ${renderList("Execution hints", data.action_hints || [])}
    ${renderExecutionBoardLanes(data.lanes || {})}
    <div class="action-row compact-actions">
      <button type="button" class="ghost-btn" onclick="loadOverdueRiskEscalations()">Overdue risk escalations</button>
      <button type="button" class="ghost-btn" onclick="loadNextReleaseReadiness()">Next release readiness</button>
      <button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button>
    </div>
    ${debugBlock(data)}`;
}

function renderExecutionBoardLanes(lanes) {
  const order = ["Escalated", "Overdue", "Due Soon", "Planned", "Unplanned", "Done"];
  return `<div class="result-list"><h4>Execution lanes</h4>${order.map(lane => {
    const items = lanes[lane] || [];
    return `<div class="result-card severity-${lane === "Escalated" || lane === "Overdue" ? "High" : (lane === "Done" ? "Low" : "Medium")}">
      <div class="result-head"><strong>${escapeHtml(lane)}</strong><span class="safe-pill">${items.length}</span></div>
      ${items.length ? items.map(item => renderExecutionBoardItem(item)).join("") : "<p>No items.</p>"}
    </div>`;
  }).join("")}</div>`;
}

function renderExecutionBoardItem(item) {
  return `<div class="small-card">
    <strong>#${item.id} ${escapeHtml(item.title)}</strong>
    <p>${escapeHtml(item.prevention_action || "Define a concrete prevention action.")}</p>
    <p>Owner: ${escapeHtml(item.owner || "Unassigned")} · Due: ${escapeHtml(item.due_date || "No due date")} · Status: ${escapeHtml(item.status)}${item.days_overdue ? ` · ${item.days_overdue} day(s) overdue` : ""}</p>
    <div class="action-row compact-actions">
      <button type="button" class="ghost-btn" onclick="updateReleaseLearningItemPlanning(${item.id})">Plan owner/due</button>
      ${item.status !== "Escalated" && !item.is_done ? `<button type="button" class="ghost-btn" onclick="escalateReleaseLearningItem(${item.id})">Escalate</button>` : ""}
      ${!item.is_done ? `<button type="button" class="ghost-btn" onclick="updateReleaseLearningItemStatus(${item.id}, 'Prevented')">Mark prevented</button>` : ""}
    </div>
  </div>`;
}

function renderOverdueRiskEscalations(data) {
  if (!data) return renderEmpty("No overdue risk escalation data available.");
  const state = data.overdue_items || data.escalated_items ? "fail" : "pass";
  return `
    <div class="readiness-card ${state}"><div><span class="readiness-label">OVERDUE RISK ESCALATIONS</span>
      <h3>${escapeHtml(data.project_name)} · ${data.escalations ? data.escalations.length : 0} escalation(s)</h3>
      <p>Shows prevention items that need release-owner attention before they let recurring risk return.</p></div></div>
    <div class="mini-grid review-summary">
      <span>Overdue <b>${data.overdue_items || 0}</b></span>
      <span>Escalated <b>${data.escalated_items || 0}</b></span>
    </div>
    ${renderList("Escalation hints", data.action_hints || [])}
    ${renderEscalationRows(data.escalations || [])}
    <div class="action-row compact-actions">
      <button type="button" class="ghost-btn" onclick="loadPreventionExecutionBoard()">Open execution board</button>
      <button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button>
    </div>
    ${debugBlock(data)}`;
}

function renderEscalationRows(rows) {
  if (!rows.length) return renderList("Escalations", ["No overdue or escalated prevention item right now."]);
  return `<div class="result-list"><h4>Escalations</h4>${rows.map(item => `
    <div class="result-card severity-${item.level === "Critical" ? "Critical" : "High"}">
      <div class="result-head"><strong>#${item.id} ${escapeHtml(item.title)}</strong><span class="safe-pill">${escapeHtml(item.level)}</span></div>
      <p>${escapeHtml(item.message)}</p>
      <p>Owner: ${escapeHtml(item.owner || "Unassigned")} · Due: ${escapeHtml(item.due_date || "No due date")} · Status: ${escapeHtml(item.status)}</p>
      <div class="action-row compact-actions">
        <button type="button" class="ghost-btn" onclick="escalateReleaseLearningItem(${item.id})">Escalate</button>
        <button type="button" class="ghost-btn" onclick="updateReleaseLearningItemPlanning(${item.id})">Re-plan</button>
      </div>
    </div>`).join("")}</div>`;
}
