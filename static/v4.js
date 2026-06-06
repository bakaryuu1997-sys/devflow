async function loadTraceability() {
  show("risks", await api(`/api/projects/${projectId}/traceability`));
  toast("Traceability matrix loaded.");
}

async function recordRequirementChange() {
  const requirement_key = document.getElementById("changeReqKey").value || "REQ-001";
  const old_text = document.getElementById("oldReqText").value;
  const new_text = document.getElementById("newReqText").value;
  show("dashboard", await api(`/api/projects/${projectId}/requirement-changes`, {
    method: "POST",
    body: JSON.stringify({ requirement_key, old_text, new_text }),
  }));
  toast("Requirement change recorded.");
}

async function runImpact() {
  const key = document.getElementById("changeReqKey").value || "REQ-001";
  show("risks", await api(`/api/projects/${projectId}/impact/${key}`));
  toast("Impact analysis completed.");
}

async function analyzeCodeRisk() {
  const files = document.getElementById("changedFiles").value.split("\n").map(x => x.trim()).filter(Boolean);
  show("risks", await api(`/api/projects/${projectId}/code-risk`, {
    method: "POST",
    body: JSON.stringify({ source: "manual", files }),
  }));
  toast("Code change risk analyzed.");
}

async function analyzeEnvGuard() {
  const content = document.getElementById("envContent").value;
  show("risks", await api(`/api/projects/${projectId}/env-guard`, {
    method: "POST",
    body: JSON.stringify({ content, required_keys: ["DATABASE_URL", "JWT_SECRET_KEY"] }),
  }));
  toast("Environment guard completed.");
}

async function loadBugPatterns() {
  show("risks", await api(`/api/projects/${projectId}/bug-patterns`));
  toast("Bug pattern dashboard loaded.");
}

async function loadAdvancedReadiness() {
  const data = await api(`/api/projects/${projectId}/advanced-readiness`);
  show("readiness", data);
  document.getElementById("metricGate").textContent = data.status === "Safe" ? "SAFE ✅" : "NOT SAFE ❌";
  document.getElementById("metricGate").style.color = data.status === "Safe" ? "#059669" : "#dc2626";
  document.getElementById("metricBlockers").textContent = data.blockers.length;
  toast("Advanced readiness calculated.");
}
