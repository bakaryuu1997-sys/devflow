async function loadReleaseReviewChecklist() {
  const data = await api(`/api/projects/${projectId}/release-review-checklist`);
  window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderEvidence(data.content));
  document.getElementById("metricGate").textContent = data.release_status;
  document.getElementById("metricBlockers").textContent = data.blocking_risks;
  toast("Release review checklist exported as Markdown.");
}
