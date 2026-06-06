const requirementPriorities = ["Low", "Medium", "High", "Critical"];
const requirementStatuses = ["Open", "In Progress", "Done", "Closed", "Archived"];
let requirementRisks = [];

async function loadRequirements() {
  const items = await api(projectPath("/requirements"));
  let workItems = [];
  try {
    workItems = await api(projectPath("/work-items"));
  } catch (_err) {
    workItems = [];
  }
  try {
    requirementRisks = await api(projectPath("/risks"));
  } catch (_err) {
    requirementRisks = [];
  }
  renderRequirements(items, workItems, requirementRisks);
  if (typeof refreshWorkItemRequirementOptions === "function") await refreshWorkItemRequirementOptions();
}

function renderRequirements(items, workItems = [], risks = []) {
  const el = document.getElementById("requirementList");
  if (!el) return;
  if (!items.length) {
    el.innerHTML = '<div class="empty-state"><strong>No requirements yet.</strong><p>Create the first requirement for this project.</p></div>';
    return;
  }
  el.innerHTML = items.map(item => {
    const linked = workItems.filter(workItem => workItem.requirement_id === item.id);
    const summary = summarizeRequirementWorkItems(linked);
    const riskSummary = summarizeRequirementRisks(risks.filter(risk => risk.requirement_id === item.id));
    const archivedClass = item.status === "Archived" ? " is-archived" : "";
    return `
      <article class="requirement-card priority-${escapeRequirementHtml(item.priority)}${archivedClass}">
        <div class="requirement-card-head">
          <div>
            <span class="requirement-key">${escapeRequirementHtml(item.key)}</span>
            <strong>${escapeRequirementHtml(item.title)}</strong>
            <small>${escapeRequirementHtml(item.priority)} · ${escapeRequirementHtml(item.status)}</small>
          </div>
          <span class="requirement-risk-pill risk-${escapeRequirementHtml(riskSummary.level)}">${riskSummary.label}</span>
        </div>
        <div class="requirement-edit-grid" aria-label="Edit requirement">
          <label>Title<input id="requirementTitleEdit-${item.id}" value="${escapeRequirementAttr(item.title)}" /></label>
          <label>Priority<select onchange="updateRequirementField(${item.id}, 'priority', this.value)">
            ${renderRequirementOptions(requirementPriorities, item.priority)}
          </select></label>
          <label>Status<select onchange="updateRequirementField(${item.id}, 'status', this.value)">
            ${renderRequirementOptions(requirementStatuses, item.status)}
          </select></label>
          <button type="button" onclick="saveRequirementTitle(${item.id})">Save title</button>
        </div>
        <div class="requirement-link-summary" aria-label="Linked work item summary">
          <span>${summary.total} linked</span>
          <span>${summary.task} task</span>
          <span>${summary.test} test</span>
          <span>${summary.bug} bug</span>
        </div>
        <div class="requirement-risk-summary" aria-label="Requirement risk summary">
          <span>${riskSummary.total} risk</span>
          <span>${riskSummary.blocking} blocking</span>
          <span>${riskSummary.highestSeverity} highest</span>
        </div>
        <div class="action-row compact-actions">
          <button type="button" class="ghost-btn" onclick="filterWorkItemsForRequirement(${item.id})">View linked work items</button>
          <button type="button" class="ghost-btn" onclick="showRequirementRisks(${item.id})">View requirement risks</button>
          <button type="button" class="ghost-btn" onclick="loadRequirementRiskDrilldown(${item.id})">Risk drilldown</button>
          <button type="button" class="ghost-btn" onclick="loadRequirementDoneGates(${item.id})">Done gates</button>
          <button type="button" class="ghost-btn danger-outline" onclick="archiveRequirementFromUi(${item.id})">Archive</button>
        </div>
      </article>
    `;
  }).join("");
}

function summarizeRequirementWorkItems(items) {
  return items.reduce((acc, item) => {
    acc.total += 1;
    if (item.kind === "task") acc.task += 1;
    if (item.kind === "test") acc.test += 1;
    if (item.kind === "bug") acc.bug += 1;
    return acc;
  }, { total: 0, task: 0, test: 0, bug: 0 });
}

function summarizeRequirementRisks(risks) {
  const rank = { Critical: 4, High: 3, Medium: 2, Low: 1 };
  const highestSeverity = risks.reduce((current, risk) => rank[risk.severity] > rank[current] ? risk.severity : current, "Low");
  const blocking = risks.filter(risk => risk.blocking).length;
  const level = blocking ? "Critical" : highestSeverity;
  const label = risks.length ? `${risks.length} risk · ${blocking} blocking` : "No active risk";
  return { total: risks.length, blocking, highestSeverity, level, label };
}

async function filterWorkItemsForRequirement(requirementId) {
  const filter = document.getElementById("workItemRequirementFilter");
  if (filter) {
    if (typeof refreshWorkItemRequirementOptions === "function") await refreshWorkItemRequirementOptions();
    filter.value = String(requirementId);
  }
  if (typeof loadWorkItems === "function") await loadWorkItems();
  toast("Filtered work items for this requirement.");
}

async function showRequirementRisks(requirementId) {
  const risks = await api(projectPath("/risks/run"), { method: "POST" });
  const selected = risks.filter(risk => risk.requirement_id === requirementId);
  show("risks", selected);
  await loadRequirements();
  toast("Requirement risks refreshed.");
}

async function createRequirementFromUi() {
  const key = document.getElementById("requirementKey").value.trim();
  const title = document.getElementById("requirementTitle").value.trim();
  const priority = document.getElementById("requirementPriority").value;
  const status = document.getElementById("requirementStatus").value;
  if (!key || !title) return toast("Requirement key and title are required.");

  await api(projectPath("/requirements"), {
    method: "POST",
    body: JSON.stringify({ key, title, priority, status }),
  });

  document.getElementById("requirementKey").value = "";
  document.getElementById("requirementTitle").value = "";
  await loadRequirements();
  await loadTraceability();
  toast("Requirement created and traceability refreshed.");
}

async function updateRequirementField(requirementId, field, value) {
  await api(`/api/requirements/${requirementId}`, {
    method: "PATCH",
    body: JSON.stringify({ [field]: value }),
  });
  await refreshAfterRequirementChange();
  toast("Requirement updated and risk visibility refreshed.");
}

async function saveRequirementTitle(requirementId) {
  const input = document.getElementById(`requirementTitleEdit-${requirementId}`);
  const title = input?.value.trim();
  if (!title) return toast("Requirement title is required.");
  await updateRequirementField(requirementId, "title", title);
}

async function archiveRequirementFromUi(requirementId) {
  await api(`/api/requirements/${requirementId}/archive`, { method: "POST" });
  await refreshAfterRequirementChange();
  toast("Requirement archived. Risk scan now ignores it.");
}

async function refreshAfterRequirementChange() {
  await loadRequirements();
  if (typeof loadWorkItems === "function") await loadWorkItems();
  if (typeof loadTraceability === "function") await loadTraceability({ navigate: false });
}

function initRequirementOptions() {
  const priority = document.getElementById("requirementPriority");
  const status = document.getElementById("requirementStatus");
  if (!priority || !status) return;
  priority.innerHTML = requirementPriorities.map(value => `<option value="${value}" ${value === "Medium" ? "selected" : ""}>${value}</option>`).join("");
  status.innerHTML = requirementStatuses.filter(value => value !== "Archived").map(value => `<option value="${value}">${value}</option>`).join("");
}

function renderRequirementOptions(values, selectedValue) {
  return values.map(value => `<option value="${escapeRequirementAttr(value)}" ${value === selectedValue ? "selected" : ""}>${escapeRequirementHtml(value)}</option>`).join("");
}

function escapeRequirementHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
}

function escapeRequirementAttr(value) {
  return escapeRequirementHtml(value).replace(/`/g, "&#96;");
}

initRequirementOptions();
