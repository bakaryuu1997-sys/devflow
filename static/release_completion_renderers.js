function renderReleaseReviewCompletion(data) {
  if (!data) return renderEmpty("No release review completion data available.");
  const rows = (data.requirements || []).map(row => `
    <div class="result-card ${row.is_done && row.review_complete ? "severity-Low" : "severity-High"}">
      <div class="result-head">
        <strong>${escapeHtml(row.requirement_key)} · ${escapeHtml(row.requirement_title)}</strong>
        <span>${row.review_complete ? '<span class="safe-pill">Reviewed</span>' : '<span class="blocker-pill">Open review</span>'}</span>
      </div>
      <div class="mini-grid">
        <span>Done gate <b>${row.is_done ? "PASS" : "WAIT"}</b></span>
        <span>Items <b>${row.done_items}/${row.linked_items}</b></span>
        <span>Open high bugs <b>${row.open_high_bugs}</b></span>
        <span>Blocking risks <b>${row.blocking_risks}</b></span>
      </div>
      ${renderDoneGates(row.gates)}
      <div class="action-row compact-actions">
        <button type="button" class="ghost-btn" onclick="loadRequirementDoneGates(${row.requirement_id})">Open gates</button>
        <button type="button" class="ghost-btn" onclick="markRequirementReviewComplete(${row.requirement_id})">Mark review complete</button>
        <button type="button" class="ghost-btn" onclick="reopenRequirementReview(${row.requirement_id})">Reopen review</button>
      </div>
    </div>`).join("");
  return `
    <div class="readiness-card ${data.release_review_complete ? "pass" : "fail"}">
      <div><span class="readiness-label">${data.release_review_complete ? "COMPLETE" : "IN REVIEW"}</span>
      <h3>Release review completion</h3><p>${data.done_requirements}/${data.total_requirements} done gates passed · ${data.reviewed_requirements}/${data.total_requirements} reviewed.</p></div>
    </div>
    <div class="mini-grid review-summary">
      <span>Done <b>${data.completion_percent}%</b></span><span>Reviewed <b>${data.review_percent}%</b></span><span>Blocking reqs <b>${data.blocking_requirements}</b></span>
    </div>
    ${renderList("Next actions", data.next_actions)}
    <div class="result-list">${rows}</div>${debugBlock(data)}`;
}

function renderRequirementDoneGates(data) {
  if (!data) return renderEmpty("No requirement gate data available.");
  return `
    <div class="readiness-card ${data.is_done ? "pass" : "fail"}">
      <div><span class="readiness-label">${data.is_done ? "DONE GATES PASS" : "GATES OPEN"}</span>
      <h3>${escapeHtml(data.requirement_key)} · ${escapeHtml(data.requirement_title)}</h3>
      <p>${data.done_items}/${data.linked_items} linked items done; review ${data.review_complete ? "complete" : "open"}.</p></div>
    </div>
    ${renderDoneGates(data.gates)}
    <div class="action-row compact-actions">
      <button type="button" class="ghost-btn" onclick="markRequirementReviewComplete(${data.requirement_id})">Mark review complete</button>
      <button type="button" class="ghost-btn" onclick="reopenRequirementReview(${data.requirement_id})">Reopen review</button>
      <button type="button" class="ghost-btn" onclick="loadRequirementRiskDrilldown(${data.requirement_id})">Risk drilldown</button>
    </div>
    ${debugBlock(data)}`;
}

function renderDoneGates(gates) {
  if (!gates || !gates.length) return "";
  return `<div class="small-section"><h4>Done gates</h4><ul>${gates.map(gate => `<li>${gate.passed ? "✅" : "⬜"} ${escapeHtml(gate.label)}</li>`).join("")}</ul></div>`;
}
