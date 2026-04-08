import { ChatRequest, ChatResponse } from "@/types/travel";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Token storage
// ---------------------------------------------------------------------------

let _accessToken: string | null = null;
let _refreshToken: string | null = null;

export function setTokens(access: string, refresh: string) {
  _accessToken = access;
  _refreshToken = refresh;
  if (typeof window !== "undefined") {
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
  }
}

export function loadTokens() {
  if (typeof window !== "undefined") {
    _accessToken = localStorage.getItem("access_token");
    _refreshToken = localStorage.getItem("refresh_token");
  }
}

export function clearTokens() {
  _accessToken = null;
  _refreshToken = null;
  if (typeof window !== "undefined") {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
  }
}

export function getAccessToken() {
  return _accessToken;
}

function authHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (_accessToken) {
    headers["Authorization"] = `Bearer ${_accessToken}`;
  }
  return headers;
}

// Prevent parallel refresh attempts
let _refreshPromise: Promise<boolean> | null = null;

async function safeRefresh(): Promise<boolean> {
  if (_refreshPromise) return _refreshPromise;
  _refreshPromise = refreshTokens().finally(() => {
    _refreshPromise = null;
  });
  return _refreshPromise;
}

async function authFetch(url: string, init?: RequestInit): Promise<Response> {
  let res = await fetch(url, {
    ...init,
    headers: { ...authHeaders(), ...(init?.headers ?? {}) },
  });

  // If 401 and we have a refresh token, try refreshing once
  if (res.status === 401 && _refreshToken) {
    const refreshed = await safeRefresh();
    if (refreshed) {
      res = await fetch(url, {
        ...init,
        headers: { ...authHeaders(), ...(init?.headers ?? {}) },
      });
    }
  }

  return res;
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  username: string;
}

interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: AuthUser;
}

export async function signUp(
  email: string,
  password: string,
  name: string,
  username: string
): Promise<AuthResponse> {
  const res = await fetch(`${API_URL}/api/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, name, username }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Erro ${res.status}`);
  }

  const data: AuthResponse = await res.json();
  if (data.access_token) {
    setTokens(data.access_token, data.refresh_token);
    if (typeof window !== "undefined") {
      localStorage.setItem("user", JSON.stringify(data.user));
    }
  }
  return data;
}

export async function signIn(
  identifier: string,
  password: string
): Promise<AuthResponse> {
  const res = await fetch(`${API_URL}/api/auth/signin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ identifier, password }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Erro ${res.status}`);
  }

  const data: AuthResponse = await res.json();
  setTokens(data.access_token, data.refresh_token);
  if (typeof window !== "undefined") {
    localStorage.setItem("user", JSON.stringify(data.user));
  }
  return data;
}

export async function refreshTokens(): Promise<boolean> {
  if (!_refreshToken) return false;

  try {
    const res = await fetch(`${API_URL}/api/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: _refreshToken }),
    });

    if (!res.ok) {
      clearTokens();
      return false;
    }

    const data: AuthResponse = await res.json();
    setTokens(data.access_token, data.refresh_token);
    if (typeof window !== "undefined") {
      localStorage.setItem("user", JSON.stringify(data.user));
    }
    return true;
  } catch {
    clearTokens();
    return false;
  }
}

export function signOut() {
  clearTokens();
}

// ---------------------------------------------------------------------------
// Chat
// ---------------------------------------------------------------------------

export async function sendMessage(req: ChatRequest): Promise<ChatResponse> {
  const res = await authFetch(`${API_URL}/api/chat`, {
    method: "POST",
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Erro ${res.status}`);
  }

  return res.json();
}

export async function clearSession(sessionId: string): Promise<void> {
  await authFetch(`${API_URL}/api/sessions/${sessionId}`, {
    method: "DELETE",
  });
}

// ---------------------------------------------------------------------------
// Sessions
// ---------------------------------------------------------------------------

export interface SessionSummary {
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface SessionWithMessages {
  session_id: string;
  title: string;
  messages: {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: string;
  }[];
}

export async function listSessions(): Promise<SessionSummary[]> {
  const res = await authFetch(`${API_URL}/api/sessions`);
  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
}

export async function getSession(
  sessionId: string
): Promise<SessionWithMessages> {
  const res = await authFetch(`${API_URL}/api/sessions/${sessionId}`);
  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
}

export async function renameSession(
  sessionId: string,
  title: string
): Promise<void> {
  await authFetch(`${API_URL}/api/sessions/${sessionId}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  });
}
