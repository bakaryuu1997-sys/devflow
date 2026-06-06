async function loadSignatureAdapterContractTests() {
  const data = await api("/api/release-governance/signature-adapter-contract-tests");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderSignatureAdapterContractTests(data));
  toast("Signature adapter contract tests loaded.");
}

async function loadSampleSignatureFixtures() {
  const data = await api("/api/release-governance/sample-signature-fixtures");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderSampleSignatureFixtures(data));
  toast("Sample signature fixtures loaded.");
}

function renderSignatureAdapterContractTests(data) {
  const cases = (data.cases || []).map(row => `${row.adapter} / ${row.fixture}: ${row.status}`);
  return `<div class="readiness-card ${data.passed ? "success" : "danger"}"><div><span class="readiness-label">ADAPTER CONTRACTS</span><h3>${escapeHtml(data.status)}</h3><p>Required fields: ${(data.required_result_fields || []).map(escapeHtml).join(", ")}</p></div></div>${renderList("Contract cases", cases)}${renderList("Blockers", data.blockers || ["No blockers."])}<div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadSampleSignatureFixtures()">Sample fixtures</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>${debugBlock(data)}`;
}

function renderSampleSignatureFixtures(data) {
  const fixtures = (data.fixtures || []).map(row => `${row.adapter} -> ${row.filename} · sha256=${row.sha256} · private key=${row.contains_private_key}`);
  return `<div class="readiness-card ${data.blockers && data.blockers.length ? "danger" : "success"}"><div><span class="readiness-label">SAFE SAMPLE FIXTURES</span><h3>${escapeHtml(data.status)}</h3><p>${data.fixture_count || 0} public/sample fixtures</p></div></div>${renderList("Fixtures", fixtures)}${renderList("Rules", data.rules || [])}<div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="loadSignatureAdapterContractTests()">Contract tests</button><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button></div>${debugBlock(data)}`;
}
