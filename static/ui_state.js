function colorizeOutput(data) {
  if (typeof data === "string") return data || "No content yet.";
  return JSON.stringify(data, null, 2)
    .replaceAll('"Critical"', '"🔴 Critical"')
    .replaceAll('"High"', '"🟠 High"')
    .replaceAll('"Medium"', '"🟡 Medium"')
    .replaceAll('"Low"', '"🟢 Low"')
    .replaceAll('"passed": true', '"passed": true ✅')
    .replaceAll('"passed": false', '"passed": false ❌');
}

function show(id, data) {
  document.getElementById(id).textContent = colorizeOutput(data);
}

function showRich(id, html) {
  document.getElementById(id).innerHTML = html;
}

function showError(id, error) {
  document.getElementById(id).textContent = `Something went wrong.\n\n${error.message || error}`;
}

function toast(message) {
  const el = document.getElementById("toast");
  el.textContent = message;
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 2800);
}

function setLoginStatus(text, kind = "neutral") {
  const el = document.getElementById("loginStatus");
  if (el) {
    el.textContent = text;
    el.className = `status-chip ${kind}`;
  }
  const loggedInDiv = document.getElementById("authLoggedIn");
  const overlay = document.getElementById("loginOverlay");
  if (loggedInDiv) {
    if (kind === "ok") {
      loggedInDiv.classList.remove("hidden");
    } else {
      loggedInDiv.classList.add("hidden");
    }
  }
  if (overlay) {
    if (kind === "ok") {
      overlay.classList.add("hidden");
    } else {
      overlay.classList.remove("hidden");
    }
  }
}

function setBusy(isBusy) {
  const el = document.getElementById("globalBusy");
  if (!el) return;
  el.classList.toggle("hidden", !isBusy);
}
