function renderTraceability(rows) {
  if (!rows || rows.length === 0) return renderEmpty("no_traceability_rows_yet");
  const html = rows.map(row => `
    <div class="result-card severity-${row.risk}">
      <div class="result-head">
        <strong>${escapeHtml(row.requirement_key)} · ${escapeHtml(row.requirement_title)}</strong>
        <span>${severityBadge(row.risk)}</span>
      </div>
      <div class="mini-grid">
        <span>${escapeHtml(t("tasks"))} <b>${row.task_count}</b></span>
        <span>${escapeHtml(t("apis"))} <b>${row.api_count}</b></span>
        <span>${escapeHtml(t("tests"))} <b>${row.test_count}</b></span>
        <span>${escapeHtml(t("bugs"))} <b>${row.bug_count}</b></span>
        <span>${escapeHtml(t("commits"))} <b>${row.commit_count}</b></span>
      </div>
      ${renderWarnings(row.warnings)}
    </div>`).join("");
  return `<div class="result-list">${html}</div>${debugBlock(rows)}`;
}

function renderReadiness(data) {
  if (!data) return renderEmpty("no_readiness_result_yet");
  const isSafe = data.status === "Safe" || data.passed === true;
  const score = data.score ?? data.readiness_score ?? "N/A";
  return `
    <div class="readiness-card ${isSafe ? "pass" : "fail"}">
      <div>
        <span class="readiness-label">${escapeHtml(t(isSafe ? "PASS" : "FAIL"))}</span>
        <h3>${escapeHtml(t(data.status || (isSafe ? "Safe" : "Not Safe")))}</h3>
        <p>${escapeHtml(t("readiness_score"))}: <b>${score}</b></p>
      </div>
    </div>
    ${renderList("blockers_title", data.blockers || [])}
    ${renderList("warnings_title", data.warnings || [])}
    ${renderList("recommendations_title", data.recommendations || [])}
    ${debugBlock(data)}`;
}

function renderFindings(items) {
  if (!items || items.length === 0) return renderEmpty("no_guard_findings_yet");
  const html = items.map(item => `
    <div class="result-card severity-${item.severity}">
      <div class="result-head">
        <strong>${escapeHtml(item.title || item.rule_id || item.key || t("finding"))}</strong>
        <span>${severityBadge(item.severity || item.risk || "Low")}</span>
      </div>
      <p>${escapeHtml(item.message || item.reason || item.status || "")}</p>
      ${item.blocking ? `<span class="blocker-pill">${escapeHtml(t("blocking"))}</span>` : `<span class="safe-pill">${escapeHtml(t("non_blocking"))}</span>`}
    </div>`).join("");
  return `<div class="result-list">${html}</div>${debugBlock(items)}`;
}

function renderReleaseRiskDashboard(data) {
  if (!data || !data.requirements || data.requirements.length === 0) return renderEmpty("no_active_requirements");
  const rows = data.requirements.map(row => `
    <div class="result-card severity-${row.highest_severity}">
      <div class="result-head">
        <strong>${escapeHtml(row.requirement_key)} · ${escapeHtml(row.requirement_title)}</strong>
        <span>${severityBadge(row.highest_severity)}</span>
      </div>
      <div class="mini-grid">
        <span>${escapeHtml(t("score"))} <b>${row.score}</b></span><span>${escapeHtml(t("risks"))} <b>${row.risk_count}</b></span>
        <span>${escapeHtml(t("blocking"))} <b>${row.blocking_risks}</b></span><span>${escapeHtml(t("priority"))} <b>${escapeHtml(t(row.priority))}</b></span>
      </div>
      ${renderList("Fix hints", row.fix_hints)}
      ${renderPlaceholderActions(row)}
      <div class="action-row compact-actions">
        <button type="button" class="ghost-btn" onclick="loadRequirementRiskDrilldown(${row.requirement_id})">${escapeHtml(t("drilldown"))}</button>
      </div>
    </div>`).join("");
  return `
    <div class="readiness-card ${data.release_status === "Safe" ? "pass" : "fail"}">
      <div><span class="readiness-label">${escapeHtml(t(data.release_status))}</span>
      <h3>${escapeHtml(t("release_risk_by_requirement"))}</h3><p>${data.total_risks} ${escapeHtml(t("risks_plural"))}, ${data.blocking_risks} ${escapeHtml(t("blocking").toLowerCase())}.</p></div>
    </div>
    ${renderList("top_actions", data.top_actions)}
    <div class="result-list">${rows}</div>${debugBlock(data)}`;
}

function renderRequirementRiskDrilldown(data) {
  if (!data) return renderEmpty("no_drilldown_data");
  return `
    <div class="readiness-card ${data.blocking_risks ? "fail" : "pass"}">
      <div><span class="readiness-label">${escapeHtml(t(data.highest_severity || "Low"))}</span>
      <h3>${escapeHtml(data.requirement_key)} · ${escapeHtml(data.requirement_title)}</h3>
      <p>${escapeHtml(t("score"))} ${data.score}; ${data.risk_count || 0} ${escapeHtml(t("risks_plural"))}, ${data.blocking_risks || 0} ${escapeHtml(t("blocking").toLowerCase())}.</p></div>
    </div>
    ${renderList("next_actions", data.next_actions)}
    ${renderDrilldownPlaceholderActions(data)}
    ${renderRiskDetails(data.risks)}
    ${renderLinkedWorkItems(data.linked_work_items)}
    ${debugBlock(data)}`;
}

function renderPlaceholderActions(row) {
  const risks = row.risks || [];
  const actions = [];
  if (risks.some(risk => risk.rule_id === "requirement_without_task")) {
    actions.push(`<button type="button" class="ghost-btn" onclick="createRequirementPlaceholder(${row.requirement_id}, 'task')">${escapeHtml(t("Create task placeholder"))}</button>`);
  }
  if (risks.some(risk => risk.rule_id === "critical_requirement_without_test")) {
    actions.push(`<button type="button" class="ghost-btn" onclick="createRequirementPlaceholder(${row.requirement_id}, 'test')">${escapeHtml(t("Create test placeholder"))}</button>`);
  }
  if (!actions.length) return "";
  return `<div class="action-row compact-actions">${actions.join("")}</div>`;
}

function renderDrilldownPlaceholderActions(data) {
  const items = data.missing_placeholders || [];
  if (!items.length) return `<div class="small-section"><h4>${escapeHtml(t("placeholder_actions"))}</h4><p class="ok-text">${escapeHtml(t("no_missing_placeholder"))}</p></div>`;
  const buttons = items.map(item => `
    <button type="button" class="ghost-btn" onclick="createRequirementPlaceholder(${data.requirement_id}, '${escapeHtml(item.kind)}')">${escapeHtml(t(item.title) || item.title)}</button>
  `).join("");
  const reasons = items.map(item => `<li>${escapeHtml(t(item.reason) || item.reason)}</li>`).join("");
  return `<div class="small-section"><h4>${escapeHtml(t("placeholder_actions"))}</h4><ul>${reasons}</ul><div class="action-row compact-actions">${buttons}</div></div>`;
}

function renderRiskDetails(risks) {
  if (!risks || !risks.length) return `<div class="small-section"><h4>${escapeHtml(t("risk_details"))}</h4><p class="ok-text">${escapeHtml(t("no_active_risks"))}</p></div>`;
  return `<div class="result-list">${risks.map(risk => `
    <div class="result-card severity-${risk.severity}">
      <div class="result-head"><strong>${escapeHtml(risk.title)}</strong><span>${severityBadge(risk.severity)}</span></div>
      <p>${escapeHtml(risk.message)}</p>
      ${risk.blocking ? `<span class="blocker-pill">${escapeHtml(t("blocking"))}</span>` : `<span class="safe-pill">${escapeHtml(t("non_blocking"))}</span>`}
    </div>`).join("")}</div>`;
}

function renderLinkedWorkItems(items) {
  if (!items || !items.length) return `<div class="small-section"><h4>${escapeHtml(t("linked_work_items"))}</h4><p class="warning-list">${escapeHtml(t("no_linked_work_items"))}</p></div>`;
  return `<div class="small-section"><h4>${escapeHtml(t("linked_work_items"))}</h4><ul>${items.map(item => `
    <li><b>${escapeHtml(t(item.kind))}</b>: ${escapeHtml(item.title)} · ${escapeHtml(t(item.status))} · ${escapeHtml(t(item.severity))} ${renderConvertPlaceholderButton(item)}</li>
  `).join("")}</ul></div>`;
}

function renderConvertPlaceholderButton(item) {
  const title = String(item.title || "");
  if (!title.toLowerCase().includes("placeholder")) return "";
  return `<button type="button" class="ghost-btn inline-action" onclick="convertPlaceholderWorkItem(${item.id}, ${jsStringArg(title)})">${escapeHtml(t("Convert placeholder"))}</button>`;
}

function jsStringArg(value) {
  return JSON.stringify(String(value || "")).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
}

function renderGeneric(data) {
  return `<pre>${escapeHtml(colorizeOutput(data))}</pre>`;
}

function renderEmpty(messageKey) {
  return `<div class="empty-state"><strong>${escapeHtml(t("empty_state"))}</strong><p>${escapeHtml(t(messageKey))}</p></div>`;
}

function renderWarnings(warnings) {
  if (!warnings || warnings.length === 0) return `<p class="ok-text">${escapeHtml(t("no_traceability_warnings"))}</p>`;
  return `<ul class="warning-list">${warnings.map(w => `<li>${escapeHtml(w)}</li>`).join("")}</ul>`;
}

function renderList(titleKey, items) {
  const displayTitle = t(titleKey);
  const noneText = t("None.");
  if (!items || items.length === 0) return `<div class="small-section"><h4>${escapeHtml(displayTitle)}</h4><p class="ok-text">${escapeHtml(noneText)}</p></div>`;
  return `<div class="small-section"><h4>${escapeHtml(displayTitle)}</h4><ul>${items.map(x => `<li>${escapeHtml(x)}</li>`).join("")}</ul></div>`;
}

function severityBadge(severity) {
  const value = severity || "Low";
  return `<span class="severity-badge severity-${escapeHtml(value)}">${escapeHtml(t(value))}</span>`;
}

function debugBlock(data) {
  return `<details class="debug-json"><summary>${escapeHtml(t("Raw JSON debug"))}</summary><pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre></details>`;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
}
