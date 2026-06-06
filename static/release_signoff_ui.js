async function loadReleaseSignoffSnapshot() {
  const data = await api(`/api/projects/${projectId}/release-signoff-snapshot`);
  showRich("readiness", renderReleaseSignoffSnapshot(data));
  document.getElementById("metricGate").textContent = data.ready_for_signoff ? "SIGN-OFF READY" : "NOT READY";
  document.getElementById("metricBlockers").textContent = (data.signoff_blockers || []).length;
  toast("Final sign-off snapshot loaded.");
}

async function createFinalReleaseSignoff() {
  const approvedBy = prompt("Approver name", "Release owner") || "Release owner";
  const approvalNote = prompt("Approval note", "Approved based on completed requirement gates and zero blocking risk.") || "";
  const data = await api(`/api/projects/${projectId}/release-signoffs`, {
    method: "POST",
    body: JSON.stringify({ approved_by: approvedBy, approval_note: approvalNote })
  });
  if (data.approval_record) window.lastEvidenceMarkdown = data.approval_record;
  showRich("readiness", renderReleaseSignoffResult(data));
  toast(data.message || "Release sign-off updated.");
}

async function loadReleaseSignoffs() {
  const data = await api(`/api/projects/${projectId}/release-signoffs`);
  showRich("readiness", renderReleaseSignoffList(data));
  toast("Release sign-off records loaded.");
}

async function loadApprovalRecord(signoffId) {
  const data = await api(`/api/release-signoffs/${signoffId}/approval-record`);
  window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderEvidence(data.content));
  toast("Approval record opened as Markdown.");
}

function renderReleaseSignoffSnapshot(data) {
  if (!data) return renderEmpty("No sign-off snapshot available.");
  const blockers = data.signoff_blockers || [];
  return `
    <div class="readiness-card ${data.ready_for_signoff ? "pass" : "fail"}">
      <div><span class="readiness-label">${data.ready_for_signoff ? "READY FOR FINAL SIGN-OFF" : "SIGN-OFF BLOCKED"}</span>
      <h3>${escapeHtml(data.project_name)} · ${escapeHtml(data.release_version)}</h3>
      <p>Decision: <b>${escapeHtml(data.decision)}</b>. Snapshot freezes review completion, risk dashboard, and checklist state.</p></div>
    </div>
    <div class="mini-grid review-summary">
      <span>Reviewed <b>${data.completion.reviewed_requirements}/${data.completion.total_requirements}</b></span>
      <span>Done gates <b>${data.completion.done_requirements}/${data.completion.total_requirements}</b></span>
      <span>Blocking risks <b>${data.risk_dashboard.blocking_risks}</b></span>
    </div>
    ${blockers.length ? renderList("Sign-off blockers", blockers) : renderList("Sign-off blockers", ["No blocker remains. Final approval can be recorded."])}
    <div class="action-row compact-actions">
      <button type="button" class="ghost-btn" onclick="createFinalReleaseSignoff()">Create final approval record</button>
      <button type="button" class="ghost-btn" onclick="loadReleaseSignoffs()">View approval records</button>
      <button type="button" class="ghost-btn" onclick="loadReleaseReviewCompletion()">Review completion</button>
    </div>
    ${debugBlock(data)}`;
}

function renderReleaseSignoffResult(data) {
  if (!data.created) {
    return `${renderReleaseSignoffSnapshot(data.snapshot)}<div class="result-card severity-High"><strong>${escapeHtml(data.message)}</strong></div>`;
  }
  return `
    <div class="readiness-card pass"><div><span class="readiness-label">APPROVAL RECORDED</span><h3>Final release sign-off created</h3><p>${escapeHtml(data.message)}</p></div></div>
    <div class="result-card severity-Low">
      <strong>${escapeHtml(data.signoff.release_version)}</strong>
      <p>Approved by ${escapeHtml(data.signoff.approved_by)} at ${escapeHtml(data.signoff.created_at || "")}</p>
      <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadApprovalRecord(${data.signoff.id})">Open approval record</button></div>
    </div>
    ${renderEvidence(data.approval_record)}`;
}

function renderReleaseSignoffList(records) {
  if (!records || !records.length) return renderEmpty("No final release sign-off approval record yet.");
  return `<div class="result-list">${records.map(row => `
    <div class="result-card severity-Low">
      <div class="result-head"><strong>${escapeHtml(row.release_version)}</strong><span class="safe-pill">Signed off</span></div>
      <p>Approved by ${escapeHtml(row.approved_by)} · ${escapeHtml(row.created_at || "")}</p>
      <p>${escapeHtml(row.approval_note || "No note")}</p>
      <button type="button" class="ghost-btn" onclick="loadApprovalRecord(${row.id})">Open approval record</button>
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="compareReleaseApprovalHistory()">Compare latest two</button><button type="button" class="ghost-btn" onclick="createReleaseRetrospectiveNote()">Create retrospective note</button></div></div>`).join("")}</div>`;
}
