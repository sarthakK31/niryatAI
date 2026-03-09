const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("niryat_token");
}

async function request(path: string, options: RequestInit = {}) {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Don't set Content-Type for FormData (browser sets boundary automatically)
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  // if (path === "/dashboard/" ) {
  //   path = "/debug";
  // }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (res.status === 401) {
    localStorage.removeItem("niryat_token");
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || "Request failed");
  }

  return res.json();
}

// Auth
export const auth = {
  register: (data: {
    email: string;
    password: string;
    full_name: string;
    company_name?: string;
    hs_codes?: string[];
    state?: string;
  }) => request("/auth/register", { method: "POST", body: JSON.stringify(data) }),

  login: (data: { email: string; password: string }) =>
    request("/auth/login", { method: "POST", body: JSON.stringify(data) }),
};

// Dashboard
export const dashboard = {
  get: () => request("/dashboard/"),
};

// Chat
export const chat = {
  sessions: () => request("/chat/sessions"),
  messages: (sessionId: string) => request(`/chat/sessions/${sessionId}/messages`),
  send: (message: string, sessionId?: string, image?: File) => {
    const form = new FormData();
    form.append("message", message);
    if (sessionId) form.append("session_id", sessionId);
    if (image) form.append("image", image);
    return request("/chat/send", { method: "POST", body: form });
  },
  deleteSession: (sessionId: string) =>
    request(`/chat/sessions/${sessionId}`, { method: "DELETE" }),
};

// Readiness
export const readiness = {
  steps: () => request("/readiness/steps"),
  summary: () => request("/readiness/summary"),
  mark: (substep_id: number, completed: boolean, notes?: string) =>
    request("/readiness/mark", {
      method: "POST",
      body: JSON.stringify({ substep_id, completed, notes }),
    }),
};

// Markets
export const markets = {
  top: (hsCode?: string) =>
    request(`/markets/top${hsCode ? `?hs_code=${hsCode}` : ""}`),
  risks: () => request("/markets/risks"),
  hsCodes: () => request("/markets/hs-codes"),
  myMarkets: () => request("/markets/my-markets"),
  mapData: () => request("/markets/map-data"),
};

// Profile
export const profile = {
  get: () => request("/profile/"),
  update: (data: {
    full_name?: string;
    company_name?: string;
    hs_codes?: string[];
    state?: string;
  }) => request("/profile/", { method: "PUT", body: JSON.stringify(data) }),
};

// HS Code Reference
export const hsCodes = {
  search: (q: string) => request(`/hs-codes/search?q=${encodeURIComponent(q)}`),
  descriptions: (codes: string[]) =>
    request("/hs-codes/descriptions", { method: "POST", body: JSON.stringify(codes) }),
};
