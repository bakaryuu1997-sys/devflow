function openEvidenceMarkdown() {
  window.open(projectPath(`/evidence.md?release_id=${releaseId}`), "_blank");
}

function openReleaseNotes() {
  window.open(releasePath("/notes"), "_blank");
}

async function initDevFlow() {
  await checkSession();
  await loadProjectSelector();
}

initDevFlow();
