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


function fillDemoLogin() {
  const email = document.getElementById("email");
  const password = document.getElementById("password");
  if (email) email.value = "admin@example.com";
  if (password) password.value = "password123";
  toast("Demo admin credentials filled for local QA only.");
}
