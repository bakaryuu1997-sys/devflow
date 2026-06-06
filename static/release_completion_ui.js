async function loadReleaseReviewCompletion() {
  const data = await api(`/api/projects/${projectId}/release-review-completion`);
  showRich("readiness", renderReleaseReviewCompletion(data));
  document.getElementById("metricGate").textContent = data.release_review_complete ? "COMPLETE" : "IN REVIEW";
  document.getElementById("metricBlockers").textContent = data.blocking_requirements;
  toast("Release review completion loaded.");
}

async function loadRequirementDoneGates(requirementId) {
  const data = await api(`/api/requirements/${requirementId}/done-gates`);
  showRich("readiness", renderRequirementDoneGates(data));
  toast("Requirement done gates loaded.");
}

async function markRequirementReviewComplete(requirementId) {
  const data = await api(`/api/requirements/${requirementId}/review-complete`, { method: "POST" });
  showRich("readiness", renderRequirementDoneGates(data));
  if (typeof loadRequirements === "function") await loadRequirements();
  toast(data.message || "Requirement review updated.");
}

async function reopenRequirementReview(requirementId) {
  const data = await api(`/api/requirements/${requirementId}/review-reopen`, { method: "POST" });
  showRich("readiness", renderRequirementDoneGates(data));
  if (typeof loadRequirements === "function") await loadRequirements();
  toast(data.message || "Requirement review reopened.");
}
