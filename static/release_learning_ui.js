async function loadReleaseLearningLoop() {
  const data = await api(`/api/projects/${projectId}/release-learning-loop`);
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderReleaseLearningLoop(data));
  toast("Release learning loop loaded.");
}

async function createReleaseLearningItemFromPrompt() {
  const payload = {
    title: prompt("Prevention item title", "Review high-risk requirements before final sign-off") || "Review high-risk requirements before final sign-off",
    prevention_action: prompt("Prevention action", "Run the requirement risk dashboard before creating approval records.") || "Run the requirement risk dashboard before creating approval records.",
    source: "manual",
    status: "Open",
    owner: prompt("Owner", "Release owner") || "",
    due_date: prompt("Due date YYYY-MM-DD", "") || ""
  };
  const data = await api(`/api/projects/${projectId}/release-learning-items`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
  toast(data.message || "Learning item saved.");
  await loadReleaseLearningLoop();
}

async function updateReleaseLearningItemStatus(itemId, status) {
  const data = await api(`/api/release-learning-items/${itemId}`, {
    method: "PATCH",
    body: JSON.stringify({ status })
  });
  toast(data.message || "Learning item updated.");
  await loadReleaseLearningLoop();
}

async function updateReleaseLearningItemPlanning(itemId) {
  const owner = prompt("Owner", "Release owner") || "";
  const dueDate = prompt("Due date YYYY-MM-DD", "") || "";
  const data = await api(`/api/release-learning-items/${itemId}/planning`, {
    method: "PATCH",
    body: JSON.stringify({ owner, due_date: dueDate })
  });
  toast(data.message || "Learning item planning updated.");
  await loadReleaseLearningLoop();
}

async function loadNextReleaseReadiness() {
  const data = await api(`/api/projects/${projectId}/next-release-readiness`);
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderNextReleaseReadiness(data));
  toast("Next release readiness loaded.");
}

function renderReleaseLearningLoop(data) {
  if (!data) return renderEmpty("No release learning loop data available.");
  return `
    <div class="readiness-card pass"><div><span class="readiness-label">RELEASE LEARNING LOOP</span>
      <h3>${escapeHtml(data.project_name)} · Prevention checklist</h3>
      <p>Turns retrospectives and recurring risk signals into a checklist for the next release.</p></div></div>
    <div class="mini-grid review-summary">
      <span>Retrospectives <b>${data.retrospective_count}</b></span>
      <span>Saved items <b>${data.saved_item_count}</b></span>
      <span>Open saved <b>${data.open_saved_item_count}</b></span>
    </div>
    ${renderRecurringRiskSignals(data.recurring_risk_signals)}
    ${renderPreventionChecklist(data.prevention_checklist)}
    ${renderSavedLearningItems(data.saved_prevention_items)}
    <div class="action-row compact-actions">
      <button type="button" class="ghost-btn" onclick="createReleaseLearningItemFromPrompt()">Add prevention item</button>
      <button type="button" class="ghost-btn" onclick="loadNextReleaseReadiness()">Next release readiness</button>
      <button type="button" class="ghost-btn" onclick="showRich('readiness', renderEvidence(window.lastEvidenceMarkdown || ''))">Open checklist Markdown</button>
      <button type="button" class="ghost-btn" onclick="createReleaseRetrospectiveNote()">Add retrospective input</button>
    </div>
    ${debugBlock(data)}`;
}

function renderRecurringRiskSignals(signals) {
  if (!signals || !signals.length) return renderList("Recurring risk signals", ["No repeated active risk pattern detected."]);
  return renderList("Recurring risk signals", signals.map(signal => `${signal.rule_id}: ${signal.count} occurrence(s), ${signal.blocking_count} blocking`));
}

function renderPreventionChecklist(items) {
  if (!items || !items.length) return renderEmpty("No prevention checklist item is needed right now.");
  return `<div class="result-list"><h4>Recurring risk prevention checklist</h4>${items.map(item => `
    <div class="result-card severity-Medium">
      <div class="result-head"><strong>${escapeHtml(item.title)}</strong><span class="safe-pill">${escapeHtml(item.source)}</span></div>
      <p>${escapeHtml(item.prevention_action)}</p>
    </div>`).join("")}</div>`;
}

function renderSavedLearningItems(items) {
  if (!items || !items.length) return renderList("Saved learning items", ["No saved learning item yet."]);
  return `<div class="result-list"><h4>Saved learning items</h4>${items.map(item => `
    <div class="result-card severity-Low">
      <div class="result-head"><strong>#${item.id} ${escapeHtml(item.title)}</strong><span class="safe-pill">${escapeHtml(item.status)}</span></div>
      <p>${escapeHtml(item.prevention_action)}</p>
      <p>Owner: ${escapeHtml(item.owner || "Unassigned")} · Due: ${escapeHtml(item.due_date || "No due date")}</p>
      <div class="action-row compact-actions">
        <button type="button" class="ghost-btn" onclick="updateReleaseLearningItemPlanning(${item.id})">Plan owner/due</button>
        <button type="button" class="ghost-btn" onclick="updateReleaseLearningItemStatus(${item.id}, 'Open')">Open</button>
        <button type="button" class="ghost-btn" onclick="updateReleaseLearningItemStatus(${item.id}, 'Done')">Done</button>
        <button type="button" class="ghost-btn" onclick="updateReleaseLearningItemStatus(${item.id}, 'Prevented')">Prevented</button>
      </div>
    </div>`).join("")}</div>`;
}


function renderNextReleaseReadiness(data) {
  if (!data) return renderEmpty("No next release readiness data available.");
  const cardState = data.status === "Ready" ? "pass" : (data.status === "At Risk" ? "fail" : "warn");
  return `
    <div class="readiness-card ${cardState}"><div><span class="readiness-label">NEXT RELEASE READINESS</span>
      <h3>${escapeHtml(data.project_name)} · ${data.score}/100</h3>
      <p>${escapeHtml(data.status)} based on open prevention items, owner coverage, due dates and overdue work.</p></div></div>
    <div class="mini-grid review-summary">
      <span>Open items <b>${data.open_items || 0}</b></span>
      <span>Planned <b>${data.planned_open_items || 0}</b></span>
      <span>Unassigned <b>${data.unassigned_items || 0}</b></span>
      <span>Overdue <b>${data.overdue_items || 0}</b></span>
    </div>
    ${renderList("Readiness hints", data.action_hints || [])}
    ${renderNextReleaseReadinessItems(data.items || [])}
    <div class="action-row compact-actions">
      <button type="button" class="ghost-btn" onclick="loadReleaseLearningLoop()">Open Learning Loop</button>
      <button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button>
    </div>
    ${debugBlock(data)}`;
}

function renderNextReleaseReadinessItems(items) {
  if (!items.length) return renderList("Prevention planning", ["No saved prevention items yet."]);
  return `<h4>Prevention planning</h4><div class="result-list">${items.map(item => `
    <div class="result-card severity-${item.is_overdue ? "High" : (item.status === "Open" ? "Medium" : "Low")}">
      <div class="result-head"><strong>#${item.id} ${escapeHtml(item.title)}</strong><span class="safe-pill">${escapeHtml(item.status)}</span></div>
      <p>${escapeHtml(item.prevention_action || "Define a concrete prevention action.")}</p>
      <p>Owner: ${escapeHtml(item.owner || "Unassigned")} · Due: ${escapeHtml(item.due_date || "No due date")} ${item.is_overdue ? "· Overdue" : ""}</p>
      <div class="action-row compact-actions">
        <button type="button" class="ghost-btn" onclick="updateReleaseLearningItemPlanning(${item.id})">Plan owner/due</button>
        <button type="button" class="ghost-btn" onclick="updateReleaseLearningItemStatus(${item.id}, 'Prevented')">Mark prevented</button>
      </div>
    </div>`).join("")}</div>`;
}
