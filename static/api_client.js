Object.defineProperty(window, "projectId", { get: () => context.projectId });
Object.defineProperty(window, "releaseId", { get: () => context.releaseId });
let accessToken = localStorage.getItem("devflow_token") || "";

function authHeaders(json = true) {
  const headers = {};
  if (json) headers["Content-Type"] = "application/json";
  if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
  return headers;
}

async function api(path, options = {}) {
  setBusy(true);
  try {
    const response = await fetch(path, { headers: authHeaders(), ...options });
    if (response.status === 401) {
      accessToken = "";
      localStorage.removeItem("devflow_token");
      if (typeof setLoginStatus === "function") {
        setLoginStatus("Session expired", "neutral");
      }
      throw new Error("Unauthorized session. Please login again.");
    }
    if (!response.ok) throw new Error(await response.text());
    return await response.json();
  } finally {
    setBusy(false);
  }
}

async function upload(path, formData) {
  setBusy(true);
  try {
    const response = await fetch(path, {
      method: "POST",
      headers: authHeaders(false),
      body: formData,
    });
    if (response.status === 401) {
      accessToken = "";
      localStorage.removeItem("devflow_token");
      if (typeof setLoginStatus === "function") {
        setLoginStatus("Session expired", "neutral");
      }
      throw new Error("Unauthorized session. Please login again.");
    }
    if (!response.ok) throw new Error(await response.text());
    return await response.json();
  } finally {
    setBusy(false);
  }
}
