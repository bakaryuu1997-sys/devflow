async function loadPublicKeyVerifierReadiness() {
  const data = await api("/api/release-governance/public-key-verifier-readiness");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderPublicKeyVerifierReadiness(data));
  toast("Public-key verifier readiness loaded.");
}

async function loadPublicKeyVerifierFixturePackage() {
  const data = await api("/api/release-governance/public-key-verifier-fixture-package");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderPublicKeyVerifierFixturePackage(data));
  toast("Public-key verifier fixture package loaded.");
}

async function runPublicKeyVerifierDryRun() {
  const data = await api("/api/release-governance/public-key-verifier-dry-run", {
    method: "POST",
    body: JSON.stringify({ use_fixture: true })
  });
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderPublicKeyVerifierDryRun(data));
  toast("Public-key verifier dry-run complete.");
}

function renderPublicKeyVerifierReadiness(data) {
  return `<div class="readiness-card ${data.ready ? "success" : "danger"}"><div><span class="readiness-label">PUBLIC-KEY VERIFIER</span><h3>${escapeHtml(data.status)}</h3><p>${escapeHtml(data.adapter || "")}</p></div></div>${renderList("Blockers", data.blockers || ["No blockers."])}${renderList("Rules", data.rules || [])}<div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="runPublicKeyVerifierDryRun()">Run fixture verify</button><button type="button" class="ghost-btn" onclick="loadPublicKeyVerifierFixturePackage()">Fixture package</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>${debugBlock(data)}`;
}

function renderPublicKeyVerifierFixturePackage(data) {
  const files = ((data.fixture || {}).files || []).map(row => `${row.name}: ${row.path} · sha256=${row.sha256}`);
  return `<div class="readiness-card ${data.blockers && data.blockers.length ? "danger" : "success"}"><div><span class="readiness-label">PUBLIC-KEY FIXTURE</span><h3>${escapeHtml(data.status)}</h3><p>${escapeHtml(data.adapter || "")}</p></div></div>${renderList("Files", files)}${renderList("Rules", data.rules || [])}${debugBlock(data)}`;
}

function renderPublicKeyVerifierDryRun(data) {
  return `<div class="readiness-card ${data.verified ? "success" : "danger"}"><div><span class="readiness-label">REAL VERIFIER DRY-RUN</span><h3>${escapeHtml(data.status)}</h3><p>verified=${data.verified}</p></div></div>${renderList("Findings", data.findings || ["No findings."])}${renderList("Next steps", data.next_steps || [])}<div class="code-block">payload=${escapeHtml(data.payload_hash || "")}\nsignature=${escapeHtml(data.signature_hash || "")}\npublic_key=${escapeHtml(data.public_key_hash || "")}</div>${debugBlock(data)}`;
}

async function loadPublicVerifierEvidencePackage() {
  const data = await api("/api/release-governance/public-verifier-evidence-package");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderPublicVerifierEvidencePackage(data));
  toast("Public verifier evidence package loaded.");
}

async function attachFixturePublicVerifierEvidence() {
  const data = await api("/api/release-governance/public-verifier-evidence-attachments", {
    method: "POST",
    body: JSON.stringify({
      signer_name: "Fixture Operator",
      key_reference: "fixtures/public_key.pem",
      evidence_reference: "fixtures/signature.b64",
      verification_payload: { use_fixture: true }
    })
  });
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderPublicVerifierEvidenceRecord(data));
  toast("Public verifier evidence attached.");
}

async function loadPublicVerifierEvidenceAttachments() {
  const data = await api("/api/release-governance/public-verifier-evidence-attachments");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderPublicVerifierEvidenceList(data));
  toast("Public verifier evidence list loaded.");
}

async function loadVerifiedSignatureApprovalGate() {
  const data = await api("/api/release-governance/verified-signature-approval-gate");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderVerifiedSignatureApprovalGate(data));
  toast("Verified-signature approval gate loaded.");
}

function renderPublicVerifierEvidencePackage(data) {
  return `<div class="readiness-card ${data.ready ? "success" : "danger"}"><div><span class="readiness-label">PUBLIC VERIFIER EVIDENCE</span><h3>${escapeHtml(data.status)}</h3><p>${escapeHtml(data.adapter || "")}</p></div></div>${renderList("Required fields", data.required_fields || [])}${renderList("Rules", data.rules || [])}<div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="attachFixturePublicVerifierEvidence()">Attach fixture evidence</button><button type="button" class="ghost-btn" onclick="loadVerifiedSignatureApprovalGate()">Open approval gate</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>${debugBlock(data)}`;
}

function renderPublicVerifierEvidenceRecord(data) {
  return `<div class="readiness-card ${data.verification_status === "Verified" ? "success" : "danger"}"><div><span class="readiness-label">VERIFIER EVIDENCE RECORD</span><h3>${escapeHtml(data.verification_status || "")}</h3><p>${escapeHtml(data.gate_status || "")}</p></div></div><div class="code-block">payload=${escapeHtml(data.payload_hash || "")}\nsignature=${escapeHtml(data.signature_hash || "")}\npublic_key=${escapeHtml(data.public_key_hash || "")}</div>${renderList("Findings", data.findings || ["No findings."])}${debugBlock(data)}`;
}

function renderPublicVerifierEvidenceList(data) {
  const rows = (data.records || []).map(row => `#${row.id} ${row.verification_status} · ${row.signer_name} · ${row.payload_hash}`);
  return `<div class="readiness-card"><div><span class="readiness-label">VERIFIER EVIDENCE</span><h3>${data.count || 0} records</h3></div></div>${renderList("Records", rows)}${debugBlock(data)}`;
}

function renderVerifiedSignatureApprovalGate(data) {
  return `<div class="readiness-card ${data.ready ? "success" : "danger"}"><div><span class="readiness-label">VERIFIED-SIGNATURE GATE</span><h3>${escapeHtml(data.status)}</h3><p>ready=${data.ready}</p></div></div>${renderList("Blockers", data.blockers || ["No blockers."])}${renderList("Approval steps", data.approval_steps || [])}${debugBlock(data)}`;
}
