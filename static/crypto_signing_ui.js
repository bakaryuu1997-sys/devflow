async function loadCryptographicSigningReadiness() {
  const data = await api("/api/release-governance/cryptographic-signing-readiness");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderCryptoSigningReadiness(data));
  toast("Cryptographic signing readiness loaded.");
}

async function loadExternalTimestampHandoffPackage() {
  const data = await api("/api/release-governance/external-timestamp-handoff-package");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderTimestampHandoffPackage(data));
  toast("Timestamp handoff package loaded.");
}

async function createExternalTimestampHandoff() {
  const payload = {
    timestamp_authority: prompt("Timestamp authority", "External TSA") || "External TSA",
    request_reference: prompt("Request/reference", "") || "",
    response_token_hash: prompt("Returned token hash, optional", "") || "",
    notes: prompt("Notes", "Payload submitted for external timestamping.") || ""
  };
  const data = await api("/api/release-governance/external-timestamp-handoffs", { method: "POST", body: JSON.stringify(payload) });
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderTimestampHandoffRecord(data));
  toast("Timestamp handoff recorded.");
}

async function loadExternalTimestampHandoffs() {
  const data = await api("/api/release-governance/external-timestamp-handoffs");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderTimestampHandoffs(data));
  toast("Timestamp handoff records loaded.");
}

async function loadTimestampHandoffIntegrityCheck() {
  const data = await api("/api/release-governance/timestamp-handoff-integrity-check");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderTimestampHandoffIntegrityCheck(data));
  toast("Timestamp handoff integrity loaded.");
}

function renderCryptoSigningReadiness(data) {
  const cls = data.ready ? "success" : "danger";
  return `<div class="readiness-card ${cls}"><div><span class="readiness-label">CRYPTO SIGNING READINESS</span><h3>${escapeHtml(data.status)}</h3><p>Payload hash: ${escapeHtml(data.payload_hash || "")}</p></div></div>${renderList("Blockers", data.blockers || [])}${renderList("Operator steps", data.operator_steps || [])}<div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadExternalTimestampHandoffPackage()">Timestamp package</button><button type="button" class="ghost-btn" onclick="createExternalTimestampHandoff()">Record handoff</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>${debugBlock(data)}`;
}

function renderTimestampHandoffPackage(data) {
  const cls = data.ready ? "success" : "danger";
  return `<div class="readiness-card ${cls}"><div><span class="readiness-label">TIMESTAMP HANDOFF</span><h3>${escapeHtml(data.status)}</h3><p>${escapeHtml(data.payload_hash || "")}</p></div></div>${renderList("Handoff steps", data.handoff_steps || [])}<div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="createExternalTimestampHandoff()">Record handoff</button><button type="button" class="ghost-btn" onclick="loadTimestampHandoffIntegrityCheck()">Verify handoff</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>${debugBlock(data)}`;
}

function renderTimestampHandoffRecord(data) {
  return `<div class="readiness-card success"><div><span class="readiness-label">TIMESTAMP HANDOFF RECORD</span><h3>${escapeHtml(data.status)}</h3><p>#${escapeHtml(String(data.id))} · ${escapeHtml(data.timestamp_authority || "")}</p></div></div>${renderList("Payload hash", [data.payload_hash || ""])}<div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadExternalTimestampHandoffs()">All handoffs</button><button type="button" class="ghost-btn" onclick="loadTimestampHandoffIntegrityCheck()">Verify handoff</button></div>${debugBlock(data)}`;
}

function renderTimestampHandoffs(data) {
  const cards = (data.records || []).map(row => `<div class="result-card"><strong>#${escapeHtml(String(row.id))} ${escapeHtml(row.status)}</strong><p>${escapeHtml(row.timestamp_authority || "")} · ${escapeHtml(row.payload_hash || "")}</p></div>`).join("");
  return `<div class="result-list"><h4>External timestamp handoffs</h4>${cards || "<p>No handoff records yet.</p>"}</div><div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="createExternalTimestampHandoff()">Record handoff</button><button type="button" class="ghost-btn" onclick="loadTimestampHandoffIntegrityCheck()">Verify latest</button></div>${debugBlock(data)}`;
}

function renderTimestampHandoffIntegrityCheck(data) {
  return `<div class="readiness-card ${data.verified ? "success" : "danger"}"><div><span class="readiness-label">TIMESTAMP HANDOFF INTEGRITY</span><h3>${escapeHtml(data.status)}</h3><p>Verified: ${escapeHtml(String(data.verified))}</p></div></div>${renderList("Current payload", [data.current_payload_hash || ""])}${renderList("Handoff payload", [data.handoff_payload_hash || "none"])}${debugBlock(data)}`;
}
