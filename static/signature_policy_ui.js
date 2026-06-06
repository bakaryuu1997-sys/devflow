async function loadSignatureVerificationAdapterStubs() {
  const data = await api("/api/release-governance/signature-verification-adapter-stubs");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderSignatureVerificationAdapterStubs(data));
  toast("Signature adapter stubs loaded.");
}

async function loadPolicyBasedVerificationChecklist() {
  const data = await api("/api/release-governance/policy-based-verification-checklist");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderPolicyBasedVerificationChecklist(data));
  toast("Policy-based verification checklist loaded.");
}

async function runSignatureAdapterDryRun() {
  const policy = await api("/api/release-governance/policy-based-verification-checklist");
  const payload = {
    adapter: prompt("Adapter", "generic-sha256-reference") || "generic-sha256-reference",
    payload_hash: prompt("Payload hash", policy.payload_hash || "") || "",
    signature_hash: prompt("Signature hash", "") || "",
    token_hash: prompt("Timestamp token hash", "") || ""
  };
  const data = await api("/api/release-governance/signature-adapter-dry-run", { method: "POST", body: JSON.stringify(payload) });
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderSignatureAdapterDryRun(data));
  toast("Signature adapter dry-run complete.");
}

function renderSignatureVerificationAdapterStubs(data) {
  const cards = (data.adapters || []).map(row => `<div class="result-card"><strong>${escapeHtml(row.name)}</strong><p>${escapeHtml(row.description)}</p><small>${escapeHtml(row.status)} · keys: ${escapeHtml(row.private_key_storage)}</small></div>`).join("");
  return `<div class="readiness-card success"><div><span class="readiness-label">VENDOR-NEUTRAL ADAPTERS</span><h3>${escapeHtml(data.status)}</h3><p>${escapeHtml(data.payload_hash || "")}</p></div></div><div class="result-list">${cards}</div>${renderList("Adapter rules", data.rules || [])}<div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="runSignatureAdapterDryRun()">Adapter dry-run</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>${debugBlock(data)}`;
}

function renderPolicyBasedVerificationChecklist(data) {
  const items = (data.checklist || []).map(item => `${item.status}: ${item.title}`);
  return `<div class="readiness-card ${data.ready ? "success" : "danger"}"><div><span class="readiness-label">POLICY VERIFICATION</span><h3>${escapeHtml(data.status)}</h3><p>${escapeHtml(data.payload_hash || "")}</p></div></div>${renderList("Checklist", items)}${renderList("Blockers", data.blockers || ["No blockers."])}<div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="runSignatureAdapterDryRun()">Adapter dry-run</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>${debugBlock(data)}`;
}

function renderSignatureAdapterDryRun(data) {
  return `<div class="readiness-card ${data.passed ? "success" : "danger"}"><div><span class="readiness-label">ADAPTER DRY-RUN</span><h3>${escapeHtml(data.status)}</h3><p>${escapeHtml(data.adapter || "")}</p></div></div>${renderList("Findings", data.findings || ["No findings."])}${renderList("Next steps", data.next_steps || [])}${debugBlock(data)}`;
}
