async function loadRequirementRiskDrilldown(requirementId) {
  const data = await api(`/api/requirements/${requirementId}/risk-drilldown`);
  showRich("readiness", renderRequirementRiskDrilldown(data));
  toast("Requirement risk drilldown loaded.");
}

async function createRequirementPlaceholder(requirementId, kind) {
  const item = await api(`/api/requirements/${requirementId}/work-item-placeholders`, {
    method: "POST",
    body: JSON.stringify({ kind }),
  });
  show("dashboard", item);
  if (typeof loadWorkItems === "function") await loadWorkItems();
  if (typeof loadRequirements === "function") await loadRequirements();
  if (typeof loadTraceability === "function") await loadTraceability({ navigate: false });
  await loadReleaseRiskDashboard();
  toast(`${kind} placeholder created or reused.`);
}


async function convertPlaceholderWorkItem(itemId, currentTitle) {
  const suggested = currentTitle
    .replace(/^Implementation task placeholder for[^:]*:\s*/i, 'Implement ')
    .replace(/^Test coverage placeholder for[^:]*:\s*/i, 'Add test coverage for ');
  const title = window.prompt('Convert placeholder into real work item title:', suggested);
  if (!title || !title.trim()) return toast('Conversion cancelled.');
  const item = await api(`/api/work-items/${itemId}/convert-placeholder`, {
    method: 'POST',
    body: JSON.stringify({ title: title.trim(), status: 'In Progress', severity: 'Medium' }),
  });
  show('dashboard', item);
  if (typeof loadWorkItems === 'function') await loadWorkItems();
  if (typeof loadRequirements === 'function') await loadRequirements();
  if (typeof loadTraceability === 'function') await loadTraceability({ navigate: false });
  await loadReleaseRiskDashboard();
  toast('Placeholder converted into real work.');
}
