const context = {
  projectId: Number(localStorage.getItem("devflow_project_id") || "1"),
  releaseId: Number(localStorage.getItem("devflow_release_id") || "1"),
};

function projectPath(path) {
  return `/api/projects/${context.projectId}${path}`;
}

function releasePath(path) {
  return `/api/releases/${context.releaseId}${path}`;
}

async function loadProjectSelector() {
  const projectSelect = document.getElementById("projectSelect");
  const releaseSelect = document.getElementById("releaseSelect");
  if (!projectSelect || !releaseSelect) return;

  const projects = await api("/api/projects");
  projectSelect.innerHTML = projects.map(project => `<option value="${project.id}">${escapeOption(project.name)}</option>`).join("");
  if (projects.length && !projects.some(project => project.id === context.projectId)) context.projectId = projects[0].id;
  projectSelect.value = String(context.projectId);

  await loadReleaseSelector();
}

async function loadReleaseSelector() {
  const releaseSelect = document.getElementById("releaseSelect");
  const releases = await api(projectPath("/releases"));
  releaseSelect.innerHTML = releases.map(release => `<option value="${release.id}">${escapeOption(release.version)}</option>`).join("");
  if (releases.length && !releases.some(release => release.id === context.releaseId)) context.releaseId = releases[0].id;
  releaseSelect.value = String(context.releaseId);
  persistContext();
}

async function changeProject() {
  context.projectId = Number(document.getElementById("projectSelect").value);
  context.releaseId = 0;
  persistContext();
  await loadReleaseSelector();
  await loadDashboard();
}

function changeRelease() {
  context.releaseId = Number(document.getElementById("releaseSelect").value);
  persistContext();
}

function persistContext() {
  localStorage.setItem("devflow_project_id", String(context.projectId));
  localStorage.setItem("devflow_release_id", String(context.releaseId));
}

function escapeOption(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
}
