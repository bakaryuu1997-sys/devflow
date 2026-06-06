async function loadSignedRehearsalArtifactPackage() {
  const data = await api("/api/release-governance/signed-rehearsal-artifact-package");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderSignedRehearsalArtifactPackage(data));
  toast("Signed rehearsal artifact package loaded.");
}

async function createSignedRehearsalArtifact() {
  const payload = {
    operator_name: prompt("Operator name", "Local Operator") || "",
    reviewer_name: prompt("Reviewer name", "Reviewer") || "",
    signature_text: prompt("Signature text", "I ran and reviewed the production upgrade rehearsal on a copied database.") || "",
    notes: prompt("Notes", "Rehearsal evidence reviewed.") || "",
  };
  const data = await api("/api/release-governance/signed-rehearsal-artifacts", { method: "POST", body: JSON.stringify(payload) });
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderSignedRehearsalArtifact(data));
  toast("Signed rehearsal artifact saved.");
}

async function loadSignedRehearsalArtifacts() {
  const data = await api("/api/release-governance/signed-rehearsal-artifacts");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderSignedRehearsalArtifacts(data));
  toast("Signed rehearsal artifacts loaded.");
}

async function createFinalOperatorApprovalRecord() {
  const payload = {
    approver_name: prompt("Approver name", "Release Approver") || "",
    approval_phrase: prompt("Approval phrase", "I_APPROVE_PRODUCTION_MIGRATION") || "",
    approval_note: prompt("Approval note", "Approved after rehearsal artifact review.") || "",
  };
  const data = await api("/api/release-governance/final-operator-approval-records", { method: "POST", body: JSON.stringify(payload) });
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderFinalOperatorApprovalRecord(data));
  toast("Final operator approval request processed.");
}

async function loadFinalOperatorApprovalRecords() {
  const data = await api("/api/release-governance/final-operator-approval-records");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderFinalOperatorApprovalRecords(data));
  toast("Final operator approval records loaded.");
}

function renderSignedRehearsalArtifactPackage(data) {
  return `<div class="readiness-card warn"><div><span class="readiness-label">SIGNED REHEARSAL PACKAGE</span><h3>${escapeHtml(data.status)}</h3><p>Artifacts: ${escapeHtml(String(data.stored_artifact_count || 0))} · Approvals: ${escapeHtml(String(data.approval_record_count || 0))}</p></div></div>
    ${renderList("Required signature", [data.required_signature_text || ""])}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="createSignedRehearsalArtifact()">Sign artifact</button><button type="button" class="ghost-btn" onclick="loadSignedRehearsalArtifacts()">Signed artifacts</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>
    ${debugBlock(data)}`;
}

function renderSignedRehearsalArtifact(data) {
  return `<div class="readiness-card ${data.status === "Signed" ? "success" : "danger"}"><div><span class="readiness-label">SIGNED ARTIFACT</span><h3>${escapeHtml(data.status)}</h3><p>Operator: ${escapeHtml(data.operator_name || "")}</p></div></div>
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="createFinalOperatorApprovalRecord()">Create final approval</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>${debugBlock(data)}`;
}

function renderSignedRehearsalArtifacts(data) {
  const cards = (data.artifacts || []).map(row => `<div class="result-card"><strong>#${escapeHtml(String(row.id))} ${escapeHtml(row.status)}</strong><p>Operator: ${escapeHtml(row.operator_name || "")} · Reviewer: ${escapeHtml(row.reviewer_name || "")}</p></div>`).join("");
  return `<div class="result-list"><h4>Signed rehearsal artifacts</h4>${cards || "<p>No artifacts yet.</p>"}</div><div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="createSignedRehearsalArtifact()">Sign artifact</button><button type="button" class="ghost-btn" onclick="createFinalOperatorApprovalRecord()">Create final approval</button></div>${debugBlock(data)}`;
}

function renderFinalOperatorApprovalRecord(data) {
  return `<div class="readiness-card ${data.status === "Approved" ? "success" : "danger"}"><div><span class="readiness-label">FINAL OPERATOR APPROVAL</span><h3>${escapeHtml(data.status)}</h3><p>${escapeHtml(data.reason || data.approver_name || "")}</p></div></div><div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadFinalOperatorApprovalRecords()">Approval records</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>${debugBlock(data)}`;
}

function renderFinalOperatorApprovalRecords(data) {
  const cards = (data.records || []).map(row => `<div class="result-card"><strong>#${escapeHtml(String(row.id))} ${escapeHtml(row.status)}</strong><p>Approver: ${escapeHtml(row.approver_name || "")} · Artifact: ${escapeHtml(String(row.signed_artifact_id || ""))}</p></div>`).join("");
  return `<div class="result-list"><h4>Final operator approval records</h4>${cards || "<p>No approval records yet.</p>"}</div><div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="createFinalOperatorApprovalRecord()">Create final approval</button></div>${debugBlock(data)}`;
}
