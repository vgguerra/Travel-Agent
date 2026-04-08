"use client";

import { useState, useCallback } from "react";
import { ChatMessage, TravelState } from "@/types/travel";
import { sendMessage, clearSession, getSession } from "@/lib/api";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [travelState, setTravelState] = useState<TravelState | null>(null);

  const send = useCallback(
    async (content: string) => {
      if (!content.trim() || loading) return;

      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setLoading(true);
      setError(null);

      try {
        const response = await sendMessage({
          message: content,
          session_id: sessionId ?? undefined,
        });

        setSessionId(response.session_id);
        setTravelState(response.state);

        const assistantMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.reply,
          timestamp: new Date(),
          state: response.state,
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Unknown error";
        setError(message);
      } finally {
        setLoading(false);
      }
    },
    [loading, sessionId]
  );

  const reset = useCallback(async () => {
    if (sessionId) await clearSession(sessionId);
    setMessages([]);
    setSessionId(null);
    setTravelState(null);
    setError(null);
  }, [sessionId]);

  const newChat = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    setTravelState(null);
    setError(null);
  }, []);

  const loadSession = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getSession(id);
      setSessionId(data.session_id);
      setMessages(
        data.messages
          .filter((m) => m.content.trim())
          .map((m) => ({
            id: m.id,
            role: m.role,
            content: m.content,
            timestamp: new Date(m.timestamp),
          }))
      );
      setTravelState(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Erro ao carregar conversa";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  return { messages, loading, error, sessionId, travelState, send, reset, newChat, loadSession };
}
