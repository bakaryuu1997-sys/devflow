async function createProjectFromSidebar() {
  const name = document.getElementById("newProjectName").value.trim();
  const description = document.getElementById("newProjectDescription").value.trim();
  if (!name) return toast("Project name is required.");

  const project = await api("/api/projects", {
    method: "POST",
    body: JSON.stringify({ name, description }),
  });

  document.getElementById("newProjectName").value = "";
  document.getElementById("newProjectDescription").value = "";
  context.projectId = project.id;
  context.releaseId = 0;
  persistContext();
  await loadProjectSelector();
  await createReleaseIfMissing(project.id);
  await loadProjectSelector();
  toast("Project created.");
}

async function createReleaseFromSidebar() {
  const version = document.getElementById("newReleaseVersion").value.trim();
  if (!version) return toast("Release version is required.");

  const release = await api(projectPath("/releases"), {
    method: "POST",
    body: JSON.stringify({ version }),
  });

  document.getElementById("newReleaseVersion").value = "";
  context.releaseId = release.id;
  persistContext();
  await loadReleaseSelector();
  toast("Release created.");
}

async function createReleaseIfMissing(projectId) {
  const releases = await api(`/api/projects/${projectId}/releases`);
  if (releases.length > 0) return;
  const release = await api(`/api/projects/${projectId}/releases`, {
    method: "POST",
    body: JSON.stringify({ version: "0.1.0" }),
  });
  context.releaseId = release.id;
  persistContext();
}
