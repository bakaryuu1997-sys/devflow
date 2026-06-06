async function loadReleaseSnapshotAnalytics() {
  const data = await api(`/api/projects/${projectId}/release-snapshot-analytics`);
  showRich("readiness", renderReleaseSnapshotAnalytics(data));
  toast("Structured release snapshot analytics loaded.");
}

async function openStructuredSnapshot(signoffId) {
  const data = await api(`/api/release-signoffs/${signoffId}/structured-snapshot`);
  showRich("readiness", renderStructuredSnapshot(data));
  toast(data.has_structured_snapshot ? "Structured snapshot opened." : "Legacy approval record converted for viewing.");
}

function renderReleaseSnapshotAnalytics(data) {
  if (!data || data.snapshot_count === 0) {
    return renderEmpty("No release sign-off snapshot exists yet.");
  }
  return `
    <div class="readiness-card pass"><div><span class="readiness-label">STRUCTURED SNAPSHOT ANALYTICS</span>
      <h3>${escapeHtml(data.latest_release_version || "No release")}</h3>
      <p>Uses stored JSON snapshots as the foundation for stronger release analytics and safer approval comparison.</p></div></div>
    <div class="mini-grid review-summary">
      <span>Snapshots <b>${data.snapshot_count}</b></span>
      <span>Structured <b>${data.structured_snapshot_count}</b></span>
      <span>Legacy <b>${data.legacy_snapshot_count}</b></span>
      <span>Requirements seen <b>${data.requirement_count_seen}</b></span>
    </div>
    ${renderSnapshotTrendRows(data.trend_rows || [])}
    ${debugBlock(data)}`;
}

function renderSnapshotTrendRows(rows) {
  if (!rows.length) return renderEmpty("No trend rows available.");
  return `<div class="result-list">${rows.map(row => `
    <div class="result-card severity-Low">
      <div class="result-head"><strong>${escapeHtml(row.release_version || "unassigned")}</strong><span class="safe-pill">${escapeHtml(row.schema_version)}</span></div>
      <p>${escapeHtml(row.created_at || "")} · Requirements ${row.done_requirements}/${row.requirements} · Blocking risks ${row.blocking_risks} · Risk events ${row.risk_events || 0}</p>
      <button type="button" class="ghost-btn" onclick="openStructuredSnapshot(${row.signoff_id})">Open structured snapshot</button>
    </div>`).join("")}</div>`;
}

function renderStructuredSnapshot(data) {
  const snap = data.structured_snapshot || {};
  const summary = snap.summary || {};
  const requirements = snap.requirements || [];
  return `
    <div class="readiness-card pass"><div><span class="readiness-label">STRUCTURED APPROVAL SNAPSHOT</span>
      <h3>${escapeHtml(snap.release?.version || data.release_version || "unassigned")}</h3>
      <p>Schema ${escapeHtml(snap.schema_version || "unknown")} · JSON snapshot is now the source for analytics.</p></div></div>
    <div class="mini-grid review-summary">
      <span>Reviewed <b>${summary.reviewed_requirements || 0}/${summary.total_requirements || requirements.length}</b></span>
      <span>Done <b>${summary.done_requirements || 0}/${summary.total_requirements || requirements.length}</b></span>
      <span>Blocking risks <b>${summary.blocking_risks || 0}</b></span>
    </div>
    ${renderList("Requirements", requirements.map(row => `${row.key}: ${row.title} · risks ${row.risk_count || 0} · events ${(row.risk_events || []).length}`))}
    ${debugBlock(data)}`;
}

async function loadReleaseRiskDeltaAnalytics() {
  const data = await api(`/api/projects/${projectId}/release-risk-delta`);
  showRich("readiness", renderReleaseRiskDeltaAnalytics(data));
  toast(data.can_compare ? "Release risk delta analytics loaded." : "Create at least two sign-offs first.");
}

function renderReleaseRiskDeltaAnalytics(data) {
  if (!data || !data.can_compare) {
    return renderEmpty(data?.message || "No release risk delta available yet.");
  }
  const summary = data.summary || {};
  return `
    <div class="readiness-card ${summary.blocking_risks_delta > 0 ? "warn" : "pass"}"><div><span class="readiness-label">RISK DELTA ANALYTICS</span>
      <h3>${escapeHtml(data.base?.release_version || "base")} → ${escapeHtml(data.target?.release_version || "target")}</h3>
      <p>Compares structured sign-off snapshots to show whether release risk improved or worsened.</p></div></div>
    <div class="mini-grid review-summary">
      <span>Total risks <b>${signedNumber(summary.total_risks_delta || 0)}</b></span>
      <span>Blocking risks <b>${signedNumber(summary.blocking_risks_delta || 0)}</b></span>
      <span>Requirements <b>${signedNumber(summary.requirement_delta || 0)}</b></span>
      <span>Done gates <b>${signedNumber(summary.done_requirements_delta || 0)}</b></span>
    </div>
    ${renderList("Action hints", data.action_hints || [])}
    ${renderRiskDeltaRows("Worsened requirements", data.worsened_requirements || [])}
    ${renderRiskDeltaRows("Improved requirements", data.improved_requirements || [])}
    ${renderRiskDeltaRows("Added requirements", data.added_requirements || [])}
    ${renderRiskDeltaRows("Removed requirements", data.removed_requirements || [])}
    ${debugBlock(data)}`;
}

function renderRiskDeltaRows(title, rows) {
  if (!rows.length) return renderList(title, ["None"]);
  return `<h4>${escapeHtml(title)}</h4><div class="result-list">${rows.map(row => `
    <div class="result-card severity-${row.blocking_risk_delta > 0 || row.risk_delta > 0 ? "High" : "Low"}">
      <div class="result-head"><strong>${escapeHtml(row.requirement_key)}</strong><span>${escapeHtml(row.requirement_title)}</span></div>
      <p>Risk ${row.base_risk_count} → ${row.target_risk_count} (${signedNumber(row.risk_delta)}) · Blocking ${row.base_blocking_risks} → ${row.target_blocking_risks} (${signedNumber(row.blocking_risk_delta)})</p>
    </div>`).join("")}</div>`;
}

function signedNumber(value) {
  const n = Number(value || 0);
  return n > 0 ? `+${n}` : `${n}`;
}


async function loadRecurringRiskTrends() {
  const data = await api(`/api/projects/${projectId}/recurring-risk-trends`);
  showRich("readiness", renderRecurringRiskTrends(data));
  toast(data.can_analyze ? "Recurring risk trends loaded." : "Create at least two sign-offs first.");
}

function renderRecurringRiskTrends(data) {
  if (!data || !data.can_analyze) {
    return renderEmpty(data?.action_hints?.[0] || "No recurring risk trend available yet.");
  }
  return `
    <div class="readiness-card ${data.recurring_risks?.length ? "warn" : "pass"}"><div><span class="readiness-label">RECURRING RISK TRENDS</span>
      <h3>${data.recurring_risks?.length || 0} recurring pattern(s)</h3>
      <p>Uses rich risk events stored inside structured sign-off snapshots to find repeated risk rules.</p></div></div>
    <div class="mini-grid review-summary">
      <span>Snapshots <b>${data.snapshot_count || 0}</b></span>
      <span>Structured <b>${data.structured_snapshot_count || 0}</b></span>
      <span>Recurring risks <b>${data.recurring_risks?.length || 0}</b></span>
      <span>Latest events <b>${data.latest_snapshot_risks?.length || 0}</b></span>
    </div>
    ${renderList("Prevention hints", data.action_hints || [])}
    ${renderRecurringRiskRows(data.recurring_risks || [])}
    ${debugBlock(data)}`;
}

function renderRecurringRiskRows(rows) {
  if (!rows.length) return renderList("Recurring risks", ["None"]);
  return `<h4>Recurring risks</h4><div class="result-list">${rows.map(row => `
    <div class="result-card severity-${escapeHtml(row.latest_severity || "Low")}">
      <div class="result-head"><strong>${escapeHtml(row.rule_id)}</strong><span>${escapeHtml(row.latest_severity || "Low")}</span></div>
      <p>${escapeHtml(row.title || "Untitled risk")} · snapshots ${row.snapshot_occurrences} · blocking ${row.blocking_occurrences}</p>
      <p>Affected: ${escapeHtml((row.affected_requirements || []).join(", ") || "none")}</p>
    </div>`).join("")}</div>`;
}


async function loadRiskPreventionBacklog() {
  const data = await api(`/api/projects/${projectId}/risk-prevention-backlog`);
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderRiskPreventionBacklog(data));
  toast(data.can_analyze ? "Risk prevention backlog loaded." : "Create at least two sign-offs first.");
}

async function autoCreateRiskPreventionItems() {
  const data = await api(`/api/projects/${projectId}/risk-prevention-backlog/auto-create`, { method: "POST" });
  showRich("readiness", renderRiskPreventionBacklog(data.backlog));
  toast(data.message || "Prevention items created.");
}

function renderRiskPreventionBacklog(data) {
  if (!data || !data.can_analyze) {
    return renderEmpty(data?.action_hints?.[0] || "No risk prevention backlog is available yet.");
  }
  return `
    <div class="readiness-card ${data.open_backlog_count ? "warn" : "pass"}"><div><span class="readiness-label">RISK PREVENTION BACKLOG</span>
      <h3>${data.open_backlog_count || 0} open prevention item(s)</h3>
      <p>Turns recurring risk trends into concrete release learning items for the next planning cycle.</p></div></div>
    <div class="mini-grid review-summary">
      <span>Snapshots <b>${data.snapshot_count || 0}</b></span>
      <span>Recurring risks <b>${data.recurring_risk_count || 0}</b></span>
      <span>Open backlog <b>${data.open_backlog_count || 0}</b></span>
      <span>Already saved <b>${data.saved_backlog_count || 0}</b></span>
    </div>
    ${renderList("Backlog hints", data.action_hints || [])}
    ${renderRiskPreventionBacklogRows(data.backlog_items || [])}
    <div class="action-row compact-actions">
      <button type="button" class="ghost-btn" onclick="autoCreateRiskPreventionItems()">Auto-create learning items</button>
      <button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button>
      <button type="button" class="ghost-btn" onclick="loadReleaseLearningLoop()">Open Learning Loop</button>
    </div>
    ${debugBlock(data)}`;
}

function renderRiskPreventionBacklogRows(rows) {
  if (!rows.length) return renderList("Risk prevention backlog", ["No recurring risk prevention item yet."]);
  return `<h4>Risk prevention backlog</h4><div class="result-list">${rows.map(row => `
    <div class="result-card severity-${escapeHtml(row.priority || "Medium")}">
      <div class="result-head"><strong>${escapeHtml(row.rule_id)}</strong><span class="safe-pill">${escapeHtml(row.priority || "Medium")}</span></div>
      <p>${escapeHtml(row.title || "Untitled prevention item")}</p>
      <p>${escapeHtml(row.prevention_action || "Define a concrete prevention action.")}</p>
      <p>Snapshots ${row.snapshot_occurrences || 0} · blocking ${row.blocking_occurrences || 0} · affected ${(row.affected_requirements || []).map(escapeHtml).join(", ") || "none"}</p>
      <p>${row.already_saved ? `Saved as learning item #${row.learning_item_id}` : "Not saved yet"}</p>
    </div>`).join("")}</div>`;
}
