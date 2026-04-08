import { ChatRequest, ChatResponse } from "@/types/travel";
import { supabase } from "./supabase";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function authHeaders(): Promise<Record<string, string>> {
  const {
    data: { session },
  } = await supabase.auth.getSession();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (session?.access_token) {
    headers["Authorization"] = `Bearer ${session.access_token}`;
  }

  return headers;
}

export async function sendMessage(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: await authHeaders(),
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Erro ${res.status}`);
  }

  return res.json();
}

export async function clearSession(sessionId: string): Promise<void> {
  await fetch(`${API_URL}/api/sessions/${sessionId}`, {
    method: "DELETE",
    headers: await authHeaders(),
  });
}

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
  const res = await fetch(`${API_URL}/api/sessions`, {
    headers: await authHeaders(),
  });

  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
}

export async function getSession(
  sessionId: string
): Promise<SessionWithMessages> {
  const res = await fetch(`${API_URL}/api/sessions/${sessionId}`, {
    headers: await authHeaders(),
  });

  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
}

export async function renameSession(
  sessionId: string,
  title: string
): Promise<void> {
  await fetch(`${API_URL}/api/sessions/${sessionId}`, {
    method: "PATCH",
    headers: await authHeaders(),
    body: JSON.stringify({ title }),
  });
}
