async function loadEvidenceManifest() {
  const data = await api("/api/release-governance/evidence-manifest");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderEvidenceManifest(data));
  toast("Evidence manifest loaded.");
}

async function freezeEvidenceManifest() {
  const payload = { notes: prompt("Manifest notes", "Evidence reviewed and ready to freeze.") || "" };
  const data = await api("/api/release-governance/evidence-manifests", { method: "POST", body: JSON.stringify(payload) });
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderFrozenEvidenceManifest(data));
  toast("Evidence manifest frozen.");
}

async function loadEvidenceManifests() {
  const data = await api("/api/release-governance/evidence-manifests");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderEvidenceManifests(data));
  toast("Frozen evidence manifests loaded.");
}

async function loadExportBundleIntegrityCheck() {
  const data = await api("/api/release-governance/export-bundle-integrity-check");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderExportBundleIntegrityCheck(data));
  toast("Bundle integrity check loaded.");
}

function renderEvidenceManifest(data) {
  return `<div class="readiness-card ${data.status === "Ready" ? "success" : "warn"}"><div><span class="readiness-label">EVIDENCE MANIFEST</span><h3>${escapeHtml(data.status)}</h3><p>Items: ${escapeHtml(String(data.item_count || 0))} · Algorithm: ${escapeHtml(data.algorithm || "sha256")}</p></div></div>
    ${renderList("Manifest hash", [data.manifest_hash || ""])}
    ${renderList("Bundle hash", [data.bundle_hash || ""])}
    <div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="freezeEvidenceManifest()">Freeze manifest</button><button type="button" class="ghost-btn" onclick="loadEvidenceManifests()">Frozen manifests</button><button type="button" class="ghost-btn" onclick="loadExportBundleIntegrityCheck()">Verify bundle</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>${debugBlock(data)}`;
}

function renderFrozenEvidenceManifest(data) {
  return `<div class="readiness-card success"><div><span class="readiness-label">FROZEN MANIFEST</span><h3>${escapeHtml(data.status)}</h3><p>#${escapeHtml(String(data.id))} · Items: ${escapeHtml(String(data.item_count || 0))}</p></div></div>${renderList("Manifest hash", [data.manifest_hash || ""])}<div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadExportBundleIntegrityCheck()">Verify bundle</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>${debugBlock(data)}`;
}

function renderEvidenceManifests(data) {
  const cards = (data.manifests || []).map(row => `<div class="result-card"><strong>#${escapeHtml(String(row.id))} ${escapeHtml(row.status)}</strong><p>Items: ${escapeHtml(String(row.item_count || 0))} · Hash: ${escapeHtml(row.manifest_hash || "")}</p></div>`).join("");
  return `<div class="result-list"><h4>Frozen evidence manifests</h4>${cards || "<p>No frozen manifests yet.</p>"}</div><div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="freezeEvidenceManifest()">Freeze current manifest</button><button type="button" class="ghost-btn" onclick="loadExportBundleIntegrityCheck()">Verify bundle</button></div>${debugBlock(data)}`;
}

function renderExportBundleIntegrityCheck(data) {
  return `<div class="readiness-card ${data.verified ? "success" : "danger"}"><div><span class="readiness-label">EXPORT BUNDLE INTEGRITY</span><h3>${escapeHtml(data.status)}</h3><p>${escapeHtml(data.reason || "")}</p></div></div>${renderList("Current manifest", [data.current_manifest_hash || ""])}${renderList("Frozen manifest", [data.frozen_manifest_hash || "none"])}<div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadEvidenceManifest()">Current manifest</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>${debugBlock(data)}`;
}
