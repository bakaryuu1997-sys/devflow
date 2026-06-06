const workItemStatuses = ["Open", "In Progress", "Done", "Closed"];
const workItemKinds = ["task", "test", "bug"];
const workItemSeverities = ["Low", "Medium", "High", "Critical"];
let workItemRequirements = [];

async function loadWorkItems() {
  await refreshWorkItemRequirementOptions();
  const items = await api(projectPath("/work-items"));
  renderWorkItems(filterWorkItems(items));
}

function filterWorkItems(items) {
  const filter = document.getElementById("workItemRequirementFilter")?.value || "all";
  if (filter === "all") return items;
  if (filter === "unlinked") return items.filter(item => !item.requirement_id);
  return items.filter(item => String(item.requirement_id) === filter);
}

function renderWorkItems(items) {
  const el = document.getElementById("workItemList");
  if (!el) return;
  if (!items.length) {
    el.innerHTML = '<div class="empty-state"><strong>No work items match this view.</strong><p>Create or filter task, test, and bug items for this project.</p></div>';
    return;
  }
  el.innerHTML = items.map(item => {
    const req = workItemRequirements.find(row => row.id === item.requirement_id);
    const reqLabel = req ? `${req.key} · ${req.title}` : "No requirement linked";
    return `
      <article class="workitem-card kind-${escapeHtml(item.kind)}">
        <div class="workitem-main">
          <span class="workitem-kind">${escapeHtml(item.kind)}</span>
          <strong>${escapeHtml(item.title)}</strong>
          <small class="workitem-link-label">${escapeHtml(reqLabel)}</small>
          <small>${escapeHtml(item.severity)} · ${escapeHtml(item.status)}</small>
        </div>
        <div class="workitem-edit-grid" aria-label="Edit work item">
          <label>Title<input id="workItemTitleEdit-${item.id}" value="${escapeAttr(item.title)}" /></label>
          <label>Status<select onchange="updateWorkItemField(${item.id}, 'status', this.value)">
            ${renderOptions(workItemStatuses, item.status)}
          </select></label>
          <label>Severity<select onchange="updateWorkItemField(${item.id}, 'severity', this.value)">
            ${renderOptions(workItemSeverities, item.severity)}
          </select></label>
          <label>Requirement<select onchange="updateWorkItemRequirement(${item.id}, this.value)">
            ${renderWorkItemRequirementOptions(item.requirement_id)}
          </select></label>
          <button type="button" onclick="saveWorkItemTitle(${item.id})">Save title</button>
        </div>
      </article>
    `;
  }).join("");
}

async function refreshWorkItemRequirementOptions() {
  workItemRequirements = (await api(projectPath("/requirements"))).filter(req => req.status !== "Archived");
  renderRequirementSelect("workItemRequirement", true);
  renderRequirementSelect("workItemRequirementFilter", false);
}

function renderRequirementSelect(id, includeNone) {
  const select = document.getElementById(id);
  if (!select) return;
  const current = select.value;
  const prefix = includeNone
    ? '<option value="">No requirement yet</option>'
    : '<option value="all">All requirements</option><option value="unlinked">Unlinked only</option>';
  select.innerHTML = prefix + workItemRequirements.map(req => (
    `<option value="${req.id}">${escapeHtml(req.key)} · ${escapeHtml(req.title)}</option>`
  )).join("");
  if ([...select.options].some(option => option.value === current)) select.value = current;
}

function renderWorkItemRequirementOptions(currentRequirementId) {
  const current = currentRequirementId == null ? "" : String(currentRequirementId);
  const none = `<option value="" ${current === "" ? "selected" : ""}>No requirement yet</option>`;
  return none + workItemRequirements.map(req => {
    const selected = String(req.id) === current ? "selected" : "";
    return `<option value="${req.id}" ${selected}>${escapeHtml(req.key)} · ${escapeHtml(req.title)}</option>`;
  }).join("");
}

function renderOptions(values, selectedValue) {
  return values.map(value => `<option value="${escapeAttr(value)}" ${value === selectedValue ? "selected" : ""}>${escapeHtml(value)}</option>`).join("");
}

async function createWorkItemFromUi() {
  const kind = document.getElementById("workItemKind").value;
  const title = document.getElementById("workItemTitle").value.trim();
  const status = document.getElementById("workItemStatus").value;
  const severity = document.getElementById("workItemSeverity").value;
  const requirementId = document.getElementById("workItemRequirement").value;
  if (!title) return toast("Work item title is required.");
  await api(projectPath("/work-items"), {
    method: "POST",
    body: JSON.stringify({ kind, title, status, severity, requirement_id: requirementId ? Number(requirementId) : null }),
  });
  document.getElementById("workItemTitle").value = "";
  await refreshAfterWorkItemChange();
  toast("Work item created and traceability refreshed.");
}

async function updateWorkItemField(itemId, field, value) {
  await api(`/api/work-items/${itemId}`, {
    method: "PATCH",
    body: JSON.stringify({ [field]: value }),
  });
  await refreshAfterWorkItemChange();
  toast("Work item updated and traceability refreshed.");
}

async function updateWorkItemRequirement(itemId, requirementId) {
  await api(`/api/work-items/${itemId}`, {
    method: "PATCH",
    body: JSON.stringify({ requirement_id: requirementId ? Number(requirementId) : null }),
  });
  await refreshAfterWorkItemChange();
  toast("Work item requirement link updated.");
}

async function saveWorkItemTitle(itemId) {
  const input = document.getElementById(`workItemTitleEdit-${itemId}`);
  const title = input?.value.trim();
  if (!title) return toast("Work item title is required.");
  await updateWorkItemField(itemId, "title", title);
}

async function updateWorkItemStatus(itemId, status) {
  await updateWorkItemField(itemId, "status", status);
}

async function refreshAfterWorkItemChange() {
  await loadWorkItems();
  if (typeof loadRequirements === "function") await loadRequirements();
  if (typeof loadTraceability === "function") await loadTraceability({ navigate: false });
}

function initWorkItemOptions() {
  const kind = document.getElementById("workItemKind");
  const status = document.getElementById("workItemStatus");
  if (!kind || !status) return;
  kind.innerHTML = workItemKinds.map(value => `<option value="${value}">${value}</option>`).join("");
  status.innerHTML = workItemStatuses.map(value => `<option value="${value}">${value}</option>`).join("");
  refreshWorkItemRequirementOptions().catch(() => {});
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/`/g, "&#96;");
}

initWorkItemOptions();
