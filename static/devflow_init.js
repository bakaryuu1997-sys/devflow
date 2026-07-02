function openEvidenceMarkdown() {
  window.open(projectPath(`/evidence.md?release_id=${releaseId}`), "_blank");
}

function openReleaseNotes() {
  window.open(releasePath("/notes"), "_blank");
}

async function initDevFlow() {
  if (typeof loadAuthSurface === "function") await loadAuthSurface();
  const config = typeof loadRuntimeConfig === "function" ? await loadRuntimeConfig() : { no_auth: false };
  if (config.no_auth && typeof enterNoAuthMode === "function") {
    enterNoAuthMode();
  } else {
    await checkSession();
  }
  await loadProjectSelector();
  if (typeof loadOperationalHistory === "function") loadOperationalHistory();
}

initDevFlow();
