let currentStep = 1;

async function safeRun(panelId, task) {
  try {
    return await task();
  } catch (error) {
    showError(panelId, error);
    toast("Action failed. Check the panel for details.");
    throw error;
  }
}

function goStep(step) {
  currentStep = step;
  for (let i = 1; i <= 6; i++) {
    document.getElementById(`step${i}`).classList.toggle("hidden-section", i !== step);
    const btn = document.getElementById(`stepBtn${i}`);
    btn.classList.toggle("active", i === step);
    btn.classList.toggle("done", i < step);
  }
  document.getElementById("metricStep").textContent = `${step} / 6`;
  document.getElementById("metricStepText").textContent = ["", "Start with demo data", "Upload and scan files", "Check requirement links", "Analyze changed requirement", "Run release gate", "Export evidence"][step];
}

async function runNextAction() {
  if (currentStep === 1) return resetDemo();
  if (currentStep === 2) return uploadHint();
  if (currentStep === 3) return loadTraceability();
  if (currentStep === 4) return runImpact();
  if (currentStep === 5) return loadAdvancedReadiness();
  return loadEvidence();
}

async function resetDemo() {
  show("dashboard", await api("/api/demo/reset", { method: "POST" }));
  document.getElementById("email").value = "admin@example.com";
  document.getElementById("password").value = "password123";
  await login();
  await loadProjectSelector();
  await loadToday();
  await loadOperationalHistory();
  goStep(2);
  toast("Step 1 complete. Upload artifacts next.");
}

async function loadToday() {
  show("dashboard", await api(`/api/projects/${projectId}/today`));
}

async function loadDashboard() {
  show("dashboard", await api(`/api/projects/${projectId}/dashboard`));
}
async function loadReleaseRiskDashboard() {
  const data = await api(`/api/projects/${projectId}/release-risk-dashboard`);
  showRich("readiness", renderReleaseRiskDashboard(data));
  document.getElementById("metricGate").textContent = data.release_status;
  document.getElementById("metricBlockers").textContent = data.blocking_risks;
  toast("Release risk dashboard refreshed by requirement.");
}

async function runRiskScan() {
  show("risks", await api(`/api/projects/${projectId}/risks/run`, { method: "POST" }));
  toast("Risk scan completed.");
}

function uploadHint() {
  goStep(2);
  toast("Choose files from examples/, then click Scan.");
}

async function uploadGuard(inputId, endpoint) {
  const file = document.getElementById(inputId).files[0];
  if (!file) return toast("Choose a file first.");
  const form = new FormData();
  form.append("file", file);
  show("risks", await upload(`/api/projects/${projectId}${endpoint}`, form));
  await loadGuards();
  toast("File scanned. Review findings or continue to traceability.");
}

async function uploadApiDiff() {
  const before = document.getElementById("apiBefore").files[0];
  const after = document.getElementById("apiAfter").files[0];
  if (!before || !after) return toast("Choose before and after OpenAPI files.");
  const form = new FormData();
  form.append("before", before);
  form.append("after", after);
  show("risks", await upload(`/api/projects/${projectId}/guards/api-diff`, form));
  await loadGuards();
}

async function loadGuards() {
  const data = await api(`/api/projects/${projectId}/guards`);
  showRich("risks", renderFindings(data));
  const blockers = data.filter((item) => item.blocking).length;
  document.getElementById("metricBlockers").textContent = blockers;
}

async function fixDemo() {
  show("dashboard", await api("/api/demo/fix", { method: "POST" }));
  await runRiskScan();
}

async function loadTraceability(options = {}) {
  if (options.navigate !== false) goStep(3);
  const data = await api(`/api/projects/${projectId}/traceability`);
  showRich("risks", renderTraceability(data));
  document.getElementById("metricTrace").textContent = "Loaded";
}

async function recordRequirementChange() {
  const requirement_key = document.getElementById("changeReqKey").value || "REQ-001";
  const old_text = document.getElementById("oldReqText").value;
  const new_text = document.getElementById("newReqText").value;
  show("dashboard", await api(`/api/projects/${projectId}/requirement-changes`, { method: "POST", body: JSON.stringify({ requirement_key, old_text, new_text }) }));
}

async function runImpact() {
  goStep(4);
  const key = document.getElementById("changeReqKey").value || "REQ-001";
  const data = await api(`/api/projects/${projectId}/impact/${key}`);
  showRich("risks", renderReadiness({
    status: "Impact Analysis",
    score: "N/A",
    blockers: data.impacted_bugs,
    warnings: data.impacted_tasks.concat(data.impacted_apis, data.impacted_tests),
    recommendations: data.suggested_actions,
  }));
}

async function analyzeCodeRisk() {
  const files = document.getElementById("changedFiles").value.split("\n").map(x => x.trim()).filter(Boolean);
  show("risks", await api(`/api/projects/${projectId}/code-risk`, { method: "POST", body: JSON.stringify({ source: "manual", files }) }));
}

async function analyzeEnvGuard() {
  const content = document.getElementById("envContent").value;
  show("risks", await api(`/api/projects/${projectId}/env-guard`, { method: "POST", body: JSON.stringify({ content, required_keys: ["DATABASE_URL", "JWT_SECRET_KEY"] }) }));
}

async function loadBugPatterns() {
  show("risks", await api(`/api/projects/${projectId}/bug-patterns`));
}

async function loadAdvancedReadiness() {
  goStep(5);
  const data = await api(`/api/projects/${projectId}/advanced-readiness`);
  showRich("readiness", renderReadiness(data));
  document.getElementById("metricGate").textContent = data.status === "Safe" ? "SAFE ✅" : "NOT SAFE ❌";
  document.getElementById("metricBlockers").textContent = data.blockers.length;
}

async function loadEvidence() {
  goStep(6);
  const data = await api(projectPath(`/evidence?release_id=${releaseId}`));
  window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderEvidence(data.content));
}

async function loadActivity() {
  const data = await api(`/api/projects/${projectId}/activity`);
  show("risks", data);
  showRich("history", renderOperationalHistory({ activity: data }));
}

async function loadOperationalHistory() {
  const panel = document.getElementById("history");
  if (!panel || !projectId || !accessToken) return;
  panel.textContent = "Loading operational history...";
  try {
    const [activity, signoffs, retrospectives] = await Promise.all([
      api(`/api/projects/${projectId}/activity`).catch(() => []),
      api(`/api/projects/${projectId}/release-signoffs`).catch(() => []),
      api(`/api/projects/${projectId}/release-retrospectives`).catch(() => []),
    ]);
    showRich("history", renderOperationalHistory({ activity, signoffs, retrospectives }));
  } catch (error) {
    showError("history", error);
  }
}

function renderOperationalHistory({ activity = [], signoffs = [], retrospectives = [] }) {
  const events = [];
  const activityItems = Array.isArray(activity) ? activity : activity.items || activity.events || [];
  activityItems.forEach((item) => events.push({
    type: item.action || item.event_type || item.kind || "Activity",
    title: item.summary || item.message || item.description || item.entity_type || "Activity event",
    meta: item.actor_email || item.actor || item.user || item.created_by || "system",
    at: item.created_at || item.timestamp || item.occurred_at,
  }));
  (Array.isArray(signoffs) ? signoffs : signoffs.items || []).forEach((item) => events.push({
    type: "Signoff",
    title: item.decision || item.status || "Release signoff",
    meta: item.signer || item.owner || item.role || "release gate",
    at: item.created_at || item.signed_at || item.timestamp,
  }));
  (Array.isArray(retrospectives) ? retrospectives : retrospectives.items || []).forEach((item) => events.push({
    type: "Retro",
    title: item.title || item.summary || item.outcome || "Release retrospective",
    meta: item.owner || item.created_by || "retro",
    at: item.created_at || item.timestamp,
  }));
  events.sort((a, b) => new Date(b.at || 0) - new Date(a.at || 0));
  if (!events.length) return '<div class="empty-history">No operational history yet. Run Reset Demo or release actions to populate the timeline.</div>';
  return `<ol class="history-list">${events.slice(0, 12).map((event) => `
    <li>
      <span class="history-type">${escapeHtml(event.type)}</span>
      <div><strong>${escapeHtml(event.title)}</strong><small>${escapeHtml(formatHistoryDate(event.at))} | ${escapeHtml(event.meta)}</small></div>
    </li>`).join("")}
  </ol>`;
}

function formatHistoryDate(value) {
  if (!value) return "time not recorded";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
}

checkSession();
goStep(1);

async function importGitCsv() {
  const content = document.getElementById("gitCsv").value;
  show("risks", await api(`/api/projects/${projectId}/git-import`, {
    method: "POST",
    body: JSON.stringify({ content, item_type: "commit" }),
  }));
  toast("Git/PR CSV imported and linked.");
}

async function runRequirementDiff() {
  const old_csv = document.getElementById("oldReqCsv").value;
  const new_csv = document.getElementById("newReqCsv").value;
  show("risks", await api(`/api/projects/${projectId}/requirement-diff`, {
    method: "POST",
    body: JSON.stringify({ old_csv, new_csv }),
  }));
  toast("Requirement versions compared.");
}

async function runDeepOpenApiDiff() {
  const before = document.getElementById("deepApiBefore").value.replaceAll("&quot;", '"');
  const after = document.getElementById("deepApiAfter").value.replaceAll("&quot;", '"');
  show("risks", await api(`/api/projects/${projectId}/openapi-deep-diff`, {
    method: "POST",
    body: JSON.stringify({ before, after }),
  }));
  toast("Deep OpenAPI diff completed.");
}

async function loadWorkload() {
  show("risks", await api(`/api/projects/${projectId}/workload`));
  toast("Workload dashboard loaded.");
}

async function verifyLedgerIntegrity() {
  try {
    const data = await api("/api/governance/verify-ledger");
    const dashboardEl = document.getElementById("dashboard");
    
    if (data.status === "verified") {
      toast(`🔒 Ledger verified: ${data.count} audit logs intact!`);
      const statusHtml = `
        <div class="ledger-status-card secure">
          <div class="ledger-status-header">
            <span class="ledger-icon">🔒</span>
            <h4>Cryptographic Ledger: SECURE</h4>
          </div>
          <p>Verified <strong>${data.count}</strong> chained audit events sequentially.</p>
          <p class="ledger-timestamp">No unauthorized SQL direct inserts, modifications, or deletions detected in activity logs.</p>
        </div>
      `;
      dashboardEl.innerHTML = statusHtml + dashboardEl.innerHTML;
    } else {
      toast("🚨 AUDIT LEDGER TAMPERED DETECTED!");
      const statusHtml = `
        <div class="ledger-status-card tampered">
          <div class="ledger-status-header">
            <span class="ledger-icon">🚨</span>
            <h4>CRYPTOGRAPHIC CHAIN: TAMPERED</h4>
          </div>
          <div class="ledger-status-body">
            <p><strong>Reason:</strong> ${data.reason}</p>
            <p><strong>Violating Record ID:</strong> ${data.record_id}</p>
            <p class="ledger-instruction">Direct database manipulation detected. Roll back to a signed baseline profile immediately!</p>
          </div>
        </div>
      `;
      dashboardEl.innerHTML = statusHtml + dashboardEl.innerHTML;
    }
  } catch (err) {
    toast("Ledger verification check failed.");
    console.error(err);
  }
}
