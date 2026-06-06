async function loadPreventionCalendarView() {
  const data = await api(`/api/projects/${projectId}/prevention-calendar-view`);
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderPreventionCalendarView(data));
  toast("Prevention calendar view loaded.");
}

async function loadReleaseReadinessTimeline() {
  const data = await api(`/api/projects/${projectId}/release-readiness-timeline`);
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderReleaseReadinessTimeline(data));
  toast("Release readiness timeline loaded.");
}

function renderPreventionCalendarView(data) {
  if (!data) return renderEmpty("No prevention calendar data available.");
  const state = data.overdue_items ? "fail" : (data.unscheduled_items ? "warn" : "pass");
  return `
    <div class="readiness-card ${state}"><div><span class="readiness-label">PREVENTION CALENDAR</span>
      <h3>${escapeHtml(data.project_name)} · ${data.scheduled_items || 0} scheduled item(s)</h3>
      <p>Shows prevention work by due date so release planning does not miss recurring-risk controls.</p></div></div>
    <div class="mini-grid review-summary">
      <span>Open <b>${data.open_items || 0}</b></span>
      <span>Scheduled <b>${data.scheduled_items || 0}</b></span>
      <span>Unscheduled <b>${data.unscheduled_items || 0}</b></span>
      <span>Overdue <b>${data.overdue_items || 0}</b></span>
    </div>
    ${renderList("Calendar hints", data.action_hints || [])}
    ${renderPreventionCalendarDays(data.calendar || [])}
    ${renderUnscheduledCalendarItems(data.unscheduled || [])}
    <div class="action-row compact-actions">
      <button type="button" class="ghost-btn" onclick="loadReleaseReadinessTimeline()">Release readiness timeline</button>
      <button type="button" class="ghost-btn" onclick="loadPreventionExecutionBoard()">Execution board</button>
      <button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button>
    </div>
    ${debugBlock(data)}`;
}

function renderPreventionCalendarDays(days) {
  if (!days.length) return renderList("Calendar", ["No scheduled prevention item yet."]);
  return `<div class="result-list"><h4>Calendar</h4>${days.map(day => `
    <div class="result-card severity-${day.bucket === "Overdue" ? "High" : (day.bucket === "This week" ? "Medium" : "Low")}">
      <div class="result-head"><strong>${escapeHtml(day.date)}</strong><span class="safe-pill">${escapeHtml(day.bucket)} · ${day.count}</span></div>
      ${day.items.map(item => renderCalendarItem(item)).join("")}
    </div>`).join("")}</div>`;
}

function renderCalendarItem(item) {
  return `<div class="small-card"><strong>#${item.id} ${escapeHtml(item.title)}</strong>
    <p>Owner: ${escapeHtml(item.owner || "Unassigned")} · Status: ${escapeHtml(item.status)} · Due in ${item.days_until_due} day(s)</p>
    <div class="action-row compact-actions">
      <button type="button" class="ghost-btn" onclick="updateReleaseLearningItemPlanning(${item.id})">Re-plan</button>
      ${!item.is_done ? `<button type="button" class="ghost-btn" onclick="updateReleaseLearningItemStatus(${item.id}, 'Prevented')">Mark prevented</button>` : ""}
    </div></div>`;
}

function renderUnscheduledCalendarItems(items) {
  if (!items.length) return "";
  return `<div class="result-list"><h4>Unscheduled prevention items</h4>${items.map(item => `
    <div class="result-card severity-High">
      <div class="result-head"><strong>#${item.id} ${escapeHtml(item.title)}</strong><span class="safe-pill">Needs due date</span></div>
      <p>Owner: ${escapeHtml(item.owner || "Unassigned")} · Status: ${escapeHtml(item.status)}</p>
      <button type="button" class="ghost-btn" onclick="updateReleaseLearningItemPlanning(${item.id})">Plan owner/due</button>
    </div>`).join("")}</div>`;
}

function renderReleaseReadinessTimeline(data) {
  if (!data) return renderEmpty("No release readiness timeline available.");
  const state = data.overall_status === "At Risk" ? "fail" : (data.overall_status === "Ready" ? "pass" : "warn");
  return `
    <div class="readiness-card ${state}"><div><span class="readiness-label">RELEASE READINESS TIMELINE</span>
      <h3>${escapeHtml(data.project_name)} · ${escapeHtml(data.overall_status)}</h3>
      <p>Projects readiness across today, 7, 14, and 30 days from prevention due dates.</p></div></div>
    <div class="mini-grid review-summary"><span>Open prevention <b>${data.open_items || 0}</b></span><span>Total <b>${data.total_items || 0}</b></span></div>
    ${renderList("Timeline hints", data.action_hints || [])}
    ${renderTimelineCheckpoints(data.checkpoints || [])}
    <div class="action-row compact-actions">
      <button type="button" class="ghost-btn" onclick="loadPreventionCalendarView()">Prevention calendar</button>
      <button type="button" class="ghost-btn" onclick="loadNextReleaseReadiness()">Next release readiness</button>
      <button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button>
    </div>
    ${debugBlock(data)}`;
}

function renderTimelineCheckpoints(rows) {
  if (!rows.length) return renderList("Timeline", ["No timeline checkpoints available."]);
  return `<div class="result-list"><h4>Timeline checkpoints</h4>${rows.map(row => `
    <div class="result-card severity-${row.status === "At Risk" ? "High" : (row.status === "On Track" ? "Low" : "Medium")}">
      <div class="result-head"><strong>${escapeHtml(row.label)} · ${escapeHtml(row.date)}</strong><span class="safe-pill">${escapeHtml(row.status)}</span></div>
      <p>Score: ${row.readiness_score} · Remaining: ${row.remaining_open_items} · Overdue by then: ${row.overdue_by_checkpoint} · Unscheduled: ${row.unscheduled_open_items}</p>
    </div>`).join("")}</div>`;
}
