const STORAGE_KEY = "devflow_workspace_state_v2";
const defaultTasks = [
  { text: "Review release blockers", done: true },
  { text: "Confirm evidence package", done: false },
  { text: "Check traceability gaps", done: false },
  { text: "Write handoff decision note", done: false },
];

const defaultTimeBlocks = [
  { time: "08:00", label: "Triage risks" },
  { time: "09:00", label: "Evidence review" },
  { time: "10:00", label: "Traceability" },
  { time: "11:00", label: "Deep QA" },
  { time: "13:00", label: "Gate sync" },
  { time: "14:00", label: "Signoff prep" },
  { time: "15:00", label: "Retro notes" },
  { time: "16:00", label: "Handoff" },
];

const baseScores = [58, 64, 70, 67, 76, 81, 84];
let state = loadState();
let timerId = null;

function defaultState() {
  return {
    tasks: structuredClone(defaultTasks),
    timeBlocks: structuredClone(defaultTimeBlocks),
    note: "",
    history: [{ text: "Workspace opened for release operations.", createdAt: new Date().toISOString() }],
    totalSeconds: 25 * 60,
    remainingSeconds: 25 * 60,
    sessionCount: 0,
  };
}

function loadState() {
  try {
    const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    return { ...defaultState(), ...parsed };
  } catch {
    return defaultState();
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function resetWorkspace() {
  if (!confirm("Reset workspace tasks, notes, history and timer?")) return;
  state = defaultState();
  saveState();
  renderAll();
}

function renderCalendar() {
  document.getElementById("calendarGrid").innerHTML = state.timeBlocks.map((block, index) => `
    <div class="time-label">${escapeText(block.time)}</div>
    <button class="time-cell ${block.label ? "busy" : ""}" onclick="editCalendarBlock(${index})">${escapeText(block.label || "Open")}</button>
  `).join("");
}

function editCalendarBlock(index) {
  const current = state.timeBlocks[index].label;
  const next = prompt(`Edit ${state.timeBlocks[index].time} block`, current);
  if (next === null) return;
  state.timeBlocks[index].label = next.trim();
  addHistory(`Updated ${state.timeBlocks[index].time} block.`);
  saveState();
  renderCalendar();
}

function renderTasks() {
  document.getElementById("taskList").innerHTML = state.tasks.map((task, index) => `
    <div class="task-item ${task.done ? "done" : ""}">
      <button class="task-check" onclick="toggleTask(${index})" aria-label="toggle task"></button>
      <span class="task-text">${escapeText(task.text)}</span>
      <button class="task-edit" onclick="editTask(${index})">Edit</button>
      <button class="task-delete" onclick="deleteTask(${index})">Delete</button>
    </div>
  `).join("");
  renderMetrics();
  renderScoreGraph();
}

function toggleTask(index) {
  state.tasks[index].done = !state.tasks[index].done;
  addHistory(`${state.tasks[index].done ? "Completed" : "Reopened"}: ${state.tasks[index].text}`);
  saveState();
  renderAll();
}

function editTask(index) {
  const next = prompt("Edit task", state.tasks[index].text);
  if (next === null || !next.trim()) return;
  state.tasks[index].text = next.trim();
  addHistory("Edited an operator checklist item.");
  saveState();
  renderAll();
}

function deleteTask(index) {
  addHistory(`Removed task: ${state.tasks[index].text}`);
  state.tasks.splice(index, 1);
  saveState();
  renderAll();
}

function addTask() {
  const input = document.getElementById("taskInput");
  const text = input.value.trim();
  if (!text) return;
  state.tasks.push({ text, done: false });
  input.value = "";
  addHistory(`Added task: ${text}`);
  saveState();
  renderAll();
}

function toggleTimer() {
  if (timerId) return pauseTimer("Paused");
  document.getElementById("timerState").textContent = "Focusing";
  timerId = setInterval(() => {
    state.remainingSeconds = Math.max(state.remainingSeconds - 1, 0);
    if (state.remainingSeconds === 0) completeSession();
    saveState();
    renderTimer();
  }, 1000);
}

function pauseTimer(label) {
  clearInterval(timerId);
  timerId = null;
  document.getElementById("timerState").textContent = label;
}

function completeSession() {
  state.sessionCount += 1;
  state.remainingSeconds = state.totalSeconds;
  addHistory("Completed a focus session.");
  pauseTimer("Completed");
  saveState();
  renderAll();
}

function resetTimer() {
  if (timerId) pauseTimer("Ready");
  state.remainingSeconds = state.totalSeconds;
  saveState();
  renderTimer();
}

function renderTimer() {
  const minutes = String(Math.floor(state.remainingSeconds / 60)).padStart(2, "0");
  const seconds = String(state.remainingSeconds % 60).padStart(2, "0");
  const progress = state.remainingSeconds / state.totalSeconds;
  document.getElementById("timerText").textContent = `${minutes}:${seconds}`;
  document.getElementById("timerRing").style.strokeDashoffset = String(364 * (1 - progress));
  document.getElementById("sessionCount").textContent = `${state.sessionCount} session${state.sessionCount === 1 ? "" : "s"}`;
  renderMetrics();
}

function saveNote() {
  state.note = document.getElementById("noteEditor").value;
  saveState();
}

function addHistoryNote() {
  const note = document.getElementById("noteEditor").value.trim();
  addHistory(note || "Manual operator checkpoint recorded.");
  saveState();
  renderAll();
}

function addHistory(text) {
  state.history = [{ text, createdAt: new Date().toISOString() }, ...(state.history || [])].slice(0, 20);
}

function renderHistory() {
  const items = state.history || [];
  document.getElementById("workspaceHistory").innerHTML = items.map(item => `
    <li><strong>${escapeText(item.text)}</strong><span>${escapeText(formatDate(item.createdAt))}</span></li>
  `).join("");
}

function renderScoreGraph() {
  const done = state.tasks.filter(task => task.done).length;
  const score = Math.min(100, 50 + done * 9 + state.sessionCount * 5 + Math.min((state.history || []).length, 8));
  const scores = baseScores.slice(1).concat(score);
  document.getElementById("scoreValue").textContent = score;
  document.getElementById("scoreHint").textContent = `${done}/${state.tasks.length} tasks done | ${state.sessionCount} focus sessions`;
  document.getElementById("scoreGraph").innerHTML = scores.map(value => `<div class="score-bar" style="height:${value}%"></div>`).join("");
}

function renderMetrics() {
  const open = state.tasks.filter(task => !task.done).length;
  document.getElementById("openTaskCount").textContent = open;
  document.getElementById("sessionCountMetric").textContent = state.sessionCount;
  document.getElementById("historyCount").textContent = (state.history || []).length;
}

function formatDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "time not recorded" : date.toLocaleString();
}

function escapeText(value) {
  return String(value).replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
}

function renderAll() {
  renderCalendar();
  renderTasks();
  renderTimer();
  renderHistory();
  renderMetrics();
  const note = document.getElementById("noteEditor");
  note.value = state.note || "";
  note.removeEventListener("input", saveNote);
  note.addEventListener("input", saveNote);
}

renderAll();
