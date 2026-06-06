async function loadSignedPayloadImportPackage() {
  const data = await api("/api/release-governance/signed-payload-import-package");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderSignedPayloadImportPackage(data));
  toast("Signed payload import package loaded.");
}

async function verifySignedPayloadImport() {
  const pkg = await api("/api/release-governance/signed-payload-import-package");
  const payload = {
    payload_hash: prompt("Payload hash", pkg.payload_hash || "") || "",
    signature_hash: prompt("Signature hash", "") || "",
    signer_name: prompt("Signer name", "Operator") || "Operator",
    signature_reference: prompt("Signature reference", "external-signature") || "external-signature",
    notes: prompt("Notes", "External signed payload imported.") || ""
  };
  const data = await api("/api/release-governance/signed-payload-verifications", { method: "POST", body: JSON.stringify(payload) });
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderSignedPayloadVerification(data));
  toast("Signed payload verification saved.");
}

async function loadSignedPayloadVerifications() {
  const data = await api("/api/release-governance/signed-payload-verifications");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderSignedPayloadVerifications(data));
  toast("Signed payload verifications loaded.");
}

async function loadTimestampTokenEvidencePackage() {
  const data = await api("/api/release-governance/timestamp-token-evidence-package");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderTimestampTokenEvidencePackage(data));
  toast("Timestamp token evidence package loaded.");
}

async function attachTimestampTokenEvidence() {
  const pkg = await api("/api/release-governance/timestamp-token-evidence-package");
  const payload = {
    payload_hash: prompt("Payload hash", pkg.payload_hash || "") || "",
    token_hash: prompt("Timestamp token hash", "") || "",
    timestamp_authority: prompt("Timestamp authority", pkg.timestamp_authority || "External TSA") || "External TSA",
    token_reference: prompt("Token/reference", "timestamp-token") || "timestamp-token",
    notes: prompt("Notes", "External timestamp token attached.") || ""
  };
  const data = await api("/api/release-governance/timestamp-token-evidence-attachments", { method: "POST", body: JSON.stringify(payload) });
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderTimestampTokenEvidenceAttachment(data));
  toast("Timestamp token evidence attached.");
}

async function loadSignedPayloadTimestampIntegrityCheck() {
  const data = await api("/api/release-governance/signed-payload-timestamp-integrity-check");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderSignedPayloadTimestampIntegrity(data));
  toast("Signed payload + timestamp integrity loaded.");
}

function renderSignedPayloadImportPackage(data) {
  return `<div class="readiness-card ${data.ready ? "success" : "danger"}"><div><span class="readiness-label">SIGNED PAYLOAD IMPORT</span><h3>${escapeHtml(data.status)}</h3><p>${escapeHtml(data.payload_hash || "")}</p></div></div>${renderList("Validation rules", data.validation_rules || [])}<div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="verifySignedPayloadImport()">Import verification</button><button type="button" class="ghost-btn" onclick="loadSignedPayloadVerifications()">All verifications</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>${debugBlock(data)}`;
}

function renderSignedPayloadVerification(data) {
  return `<div class="readiness-card ${data.verification_status === "Verified" ? "success" : "danger"}"><div><span class="readiness-label">SIGNED PAYLOAD VERIFICATION</span><h3>${escapeHtml(data.verification_status)}</h3><p>${escapeHtml(data.signer_name || "")}</p></div></div>${renderList("Payload hash", [data.payload_hash || ""])}${debugBlock(data)}`;
}

function renderSignedPayloadVerifications(data) {
  const cards = (data.records || []).map(row => `<div class="result-card"><strong>#${escapeHtml(String(row.id))} ${escapeHtml(row.verification_status)}</strong><p>${escapeHtml(row.signer_name || "")} · ${escapeHtml(row.payload_hash || "")}</p></div>`).join("");
  return `<div class="result-list"><h4>Signed payload verifications</h4>${cards || "<p>No signed payload verifications yet.</p>"}</div>${debugBlock(data)}`;
}

function renderTimestampTokenEvidencePackage(data) {
  return `<div class="readiness-card ${data.ready ? "success" : "danger"}"><div><span class="readiness-label">TIMESTAMP TOKEN EVIDENCE</span><h3>${escapeHtml(data.status)}</h3><p>${escapeHtml(data.payload_hash || "")}</p></div></div>${renderList("Validation rules", data.validation_rules || [])}<div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="attachTimestampTokenEvidence()">Attach token evidence</button><button type="button" class="ghost-btn" onclick="loadSignedPayloadTimestampIntegrityCheck()">Verify all</button></div>${debugBlock(data)}`;
}

function renderTimestampTokenEvidenceAttachment(data) {
  return `<div class="readiness-card ${data.verification_status === "Verified" ? "success" : "danger"}"><div><span class="readiness-label">TOKEN EVIDENCE ATTACHMENT</span><h3>${escapeHtml(data.verification_status)}</h3><p>${escapeHtml(data.timestamp_authority || "")}</p></div></div>${renderList("Payload hash", [data.payload_hash || ""])}${debugBlock(data)}`;
}

function renderSignedPayloadTimestampIntegrity(data) {
  return `<div class="readiness-card ${data.verified ? "success" : "danger"}"><div><span class="readiness-label">SIGNED PAYLOAD + TIMESTAMP</span><h3>${escapeHtml(data.status)}</h3><p>Verified: ${escapeHtml(String(data.verified))}</p></div></div>${renderList("Checks", [`Signed payload: ${data.signed_payload_verified}`, `Timestamp token: ${data.timestamp_token_verified}`])}${debugBlock(data)}`;
}
