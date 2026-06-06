async function compareReleaseApprovalHistory() {
  const data = await api(`/api/projects/${projectId}/release-signoffs/compare`);
  if (data.summary_markdown) window.lastEvidenceMarkdown = data.summary_markdown;
  showRich("readiness", renderReleaseApprovalCompare(data));
  toast(data.can_compare ? "Approval history compared." : "Need at least two approval records to compare.");
}

async function createReleaseRetrospectiveNote() {
  const signoffIdRaw = prompt("Sign-off ID to attach, blank for latest/general", "") || "";
  const payload = {
    signoff_id: signoffIdRaw.trim() ? Number(signoffIdRaw.trim()) : null,
    author: prompt("Retrospective author", "Release owner") || "Release owner",
    what_went_well: prompt("What went well?", "Release gates were reviewed before approval.") || "",
    what_to_improve: prompt("What should improve next time?", "Reduce late requirement risk before sign-off.") || "",
    action_items: prompt("Action items", "Review high-risk requirements earlier in the next release.") || ""
  };
  const data = await api(`/api/projects/${projectId}/release-retrospectives`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderReleaseRetrospectiveResult(data));
  toast(data.message || "Retrospective note saved.");
}

async function loadReleaseRetrospectives() {
  const data = await api(`/api/projects/${projectId}/release-retrospectives`);
  showRich("readiness", renderReleaseRetrospectiveList(data));
  toast("Retrospective notes loaded.");
}

async function openReleaseRetrospective(noteId) {
  const data = await api(`/api/release-retrospectives/${noteId}/export`);
  window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderEvidence(data.content));
  toast("Retrospective note opened as Markdown.");
}

function renderReleaseApprovalCompare(data) {
  if (!data || !data.can_compare) {
    return `<div class="result-card severity-Medium"><strong>Approval history compare not ready</strong><p>${escapeHtml(data?.message || "Create at least two approval records first.")}</p></div>`;
  }
  return `
    <div class="readiness-card pass"><div><span class="readiness-label">APPROVAL HISTORY COMPARE</span>
      <h3>${escapeHtml(data.base.release_version)} → ${escapeHtml(data.target.release_version)}</h3>
      <p>Compares final approval records so the team can see what changed between releases or sign-off snapshots.</p></div></div>
    <div class="mini-grid review-summary">
      <span>Added <b>${data.added_requirements.length}</b></span>
      <span>Removed <b>${data.removed_requirements.length}</b></span>
      <span>Unchanged <b>${data.unchanged_requirements.length}</b></span>
    </div>
    ${renderList("Added requirements", data.added_requirements.map(row => `${row.requirement_key}: ${row.requirement_title}`))}
    ${renderList("Removed requirements", data.removed_requirements.map(row => `${row.requirement_key}: ${row.requirement_title}`))}
    <div class="action-row compact-actions">
      <button type="button" class="ghost-btn" onclick="showRich('readiness', renderEvidence(window.lastEvidenceMarkdown || ''))">Open compare Markdown</button>
      <button type="button" class="ghost-btn" onclick="createReleaseRetrospectiveNote()">Create retrospective note</button>
      <button type="button" class="ghost-btn" onclick="loadReleaseRetrospectives()">View retrospectives</button>
    </div>
    ${debugBlock(data)}`;
}

function renderReleaseRetrospectiveResult(data) {
  if (!data.created) return `<div class="result-card severity-High"><strong>${escapeHtml(data.message || "Retrospective note was not saved.")}</strong></div>`;
  return `
    <div class="readiness-card pass"><div><span class="readiness-label">RETROSPECTIVE SAVED</span><h3>Post-release note recorded</h3><p>${escapeHtml(data.message)}</p></div></div>
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="openReleaseRetrospective(${data.note.id})">Open retrospective Markdown</button><button type="button" class="ghost-btn" onclick="loadReleaseRetrospectives()">View all retrospectives</button></div>
    ${renderEvidence(data.content)}`;
}

function renderReleaseRetrospectiveList(notes) {
  if (!notes || !notes.length) return renderEmpty("No post-release retrospective note yet.");
  return `<div class="result-list">${notes.map(note => `
    <div class="result-card severity-Low">
      <div class="result-head"><strong>Retrospective #${note.id}</strong><span class="safe-pill">Post-release</span></div>
      <p>Author: ${escapeHtml(note.author)} · ${escapeHtml(note.created_at || "")}</p>
      <p><b>Went well:</b> ${escapeHtml(note.what_went_well || "—")}</p>
      <p><b>Improve:</b> ${escapeHtml(note.what_to_improve || "—")}</p>
      <button type="button" class="ghost-btn" onclick="openReleaseRetrospective(${note.id})">Open retrospective</button>
    </div>`).join("")}</div>`;
}
