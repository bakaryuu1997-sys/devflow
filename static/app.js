const LOCAL_SAMPLE_CREDENTIALS = Object.freeze({
  email: "admin@example.com",
  password: "password123",
});

let authSurface = { authMode: "unknown", isProduction: false, checks: [] };

async function registerAccount() {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  if (!email) return toast("Email is required.");
  if (password.length < 8) return toast("Password must be at least 8 characters.");
  try {
    await api("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, role: "viewer" }),
    });
    await login();
    toast("Account created.");
  } catch (error) {
    toast(String(error).includes("409") ? "Account already exists. Please login." : error.message);
  }
}

async function login() {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  if (!email || !password) return toast("Email and password are required.");
  const data = await api("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  accessToken = data.access_token;
  localStorage.setItem("devflow_token", accessToken);
  setLoginStatus(`Logged in as ${email}`, "ok");
  if (typeof loadOperationalHistory === "function") loadOperationalHistory();
}

function logout() {
  accessToken = "";
  localStorage.removeItem("devflow_token");
  setLoginStatus("Logged out", "neutral");
}

async function loadLocalStats() {
  const el = document.getElementById("localStats");
  if (!el) return;
  try {
    const stats = await api("/api/local/stats");
    const tableCount = Object.keys(stats.tables || {}).length;
    el.innerHTML = `<strong>Local database</strong><span>${stats.total_rows} rows across ${tableCount} tables</span>`;
  } catch {
    el.innerHTML = "<span>Data stats unavailable.</span>";
  }
}

async function resetAllData() {
  const ok = confirm(
    "This deletes ALL local data (projects, releases, history) and re-seeds the default admin. Continue?",
  );
  if (!ok) return;
  try {
    await api("/api/local/reset-all", { method: "POST" });
    toast("All local data was reset.");
    setTimeout(() => window.location.reload(), 800);
  } catch (error) {
    toast("Reset failed: " + (error.message || error));
  }
}

async function loadRuntimeConfig() {
  try {
    return await api("/api/auth/config");
  } catch {
    return { no_auth: false, login_required: true };
  }
}

// Local personal-use mode: the server accepts requests as the default admin,
// so we skip the login overlay entirely and go straight into the app.
function enterNoAuthMode() {
  accessToken = "local-no-auth"; // sentinel so client-side gates pass; server ignores the value
  const overlay = document.getElementById("loginOverlay");
  if (overlay) overlay.classList.add("hidden");
  const loggedIn = document.getElementById("authLoggedIn");
  if (loggedIn) loggedIn.classList.add("hidden");
  const guide = document.getElementById("howToUse");
  if (guide) guide.hidden = false;
}

async function checkSession() {
  if (!accessToken) return setLoginStatus("Not logged in", "neutral");
  try {
    const me = await api("/api/auth/me");
    setLoginStatus(`Logged in as ${me.email}`, "ok");
    if (typeof loadOperationalHistory === "function") loadOperationalHistory();
  } catch {
    logout();
  }
}

async function loadAuthSurface() {
  try {
    const data = await api("/api/security/checklist");
    authSurface = {
      authMode: data.auth_mode || "unknown",
      isProduction: data.auth_mode === "production",
      checks: Array.isArray(data.checks) ? data.checks : [],
    };
  } catch {
    authSurface = { authMode: "unknown", isProduction: false, checks: [] };
  }
  renderAuthSurface();
}

function renderAuthSurface() {
  const modeLabel = authSurface.isProduction ? "Production auth" : "Local QA auth";
  const sampleHint = authSurface.isProduction
    ? "Sample credentials are hidden in production mode."
    : "Sample credentials only seed the isolated local QA account.";
  const resetLabel = authSurface.isProduction
    ? "Sample seed disabled in production"
    : "Initialize Local Sample Workspace";

  setText("authModeChip", modeLabel);
  setText("localSampleHint", sampleHint);

  const chip = document.getElementById("authModeChip");
  if (chip) chip.classList.toggle("warning", !authSurface.isProduction);

  const sampleButton = document.getElementById("localSampleLogin");
  if (sampleButton) {
    sampleButton.hidden = authSurface.isProduction;
    sampleButton.disabled = authSurface.isProduction;
  }

  const resetButton = document.getElementById("resetDemoButton");
  if (resetButton) {
    resetButton.disabled = authSurface.isProduction;
    resetButton.textContent = resetLabel;
    resetButton.title = authSurface.isProduction
      ? "Production mode blocks local sample resets."
      : "Creates deterministic local QA data and signs in the local admin.";
  }
}

function isProductionAuthSurface() {
  return authSurface.isProduction;
}

function fillLocalSampleLogin() {
  if (isProductionAuthSurface()) {
    toast("Local sample credentials are disabled in production.");
    return false;
  }
  const email = document.getElementById("email");
  const password = document.getElementById("password");
  if (email) email.value = LOCAL_SAMPLE_CREDENTIALS.email;
  if (password) password.value = LOCAL_SAMPLE_CREDENTIALS.password;
  toast("Local sample credentials filled for isolated QA only.");
  return true;
}

function fillDemoLogin() {
  return fillLocalSampleLogin();
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) element.textContent = value;
}
