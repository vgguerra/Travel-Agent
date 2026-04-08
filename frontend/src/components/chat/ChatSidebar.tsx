"use client";

import { useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  MessageSquare,
  Plus,
  Trash2,
  PanelLeftClose,
  PanelLeft,
} from "lucide-react";
import { listSessions, clearSession, SessionSummary } from "@/lib/api";

interface ChatSidebarProps {
  currentSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onNewChat: () => void;
  isOpen: boolean;
  onToggle: () => void;
}

export function ChatSidebar({
  currentSessionId,
  onSelectSession,
  onNewChat,
  isOpen,
  onToggle,
}: ChatSidebarProps) {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listSessions();
      setSessions(data);
    } catch {
      // silently fail — sidebar is non-critical
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh, currentSessionId]);

  const handleDelete = async (
    e: React.MouseEvent,
    sessionId: string
  ) => {
    e.stopPropagation();
    await clearSession(sessionId);
    if (sessionId === currentSessionId) {
      onNewChat();
    }
    setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));
  };

  const formatDate = (iso: string) => {
    const d = new Date(iso);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    const days = Math.floor(diff / 86400000);

    if (days === 0) return "Hoje";
    if (days === 1) return "Ontem";
    if (days < 7) return `${days}d atras`;
    return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
  };

  // Collapsed toggle button
  if (!isOpen) {
    return (
      <button
        onClick={onToggle}
        className="absolute top-3 left-3 z-30 w-8 h-8 rounded-lg flex items-center justify-center
          text-white/30 hover:text-white hover:bg-white/5 transition-colors"
        title="Abrir historico"
      >
        <PanelLeft size={16} />
      </button>
    );
  }

  return (
    <motion.aside
      initial={{ width: 0, opacity: 0 }}
      animate={{ width: 280, opacity: 1 }}
      exit={{ width: 0, opacity: 0 }}
      transition={{ duration: 0.2 }}
      className="shrink-0 h-full border-r border-white/5 bg-[var(--background)] flex flex-col overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3 h-14 border-b border-white/5">
        <span className="text-white/50 text-xs font-medium uppercase tracking-wider">
          Historico
        </span>
        <div className="flex items-center gap-1">
          <button
            onClick={onNewChat}
            className="w-7 h-7 rounded-md flex items-center justify-center
              text-white/30 hover:text-white hover:bg-white/5 transition-colors"
            title="Nova conversa"
          >
            <Plus size={14} />
          </button>
          <button
            onClick={onToggle}
            className="w-7 h-7 rounded-md flex items-center justify-center
              text-white/30 hover:text-white hover:bg-white/5 transition-colors"
            title="Fechar historico"
          >
            <PanelLeftClose size={14} />
          </button>
        </div>
      </div>

      {/* Session list */}
      <div className="flex-1 overflow-y-auto py-2 px-2 space-y-0.5">
        {loading && sessions.length === 0 ? (
          <div className="flex items-center justify-center py-8">
            <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : sessions.length === 0 ? (
          <p className="text-white/20 text-xs text-center py-8">
            Nenhuma conversa ainda
          </p>
        ) : (
          <AnimatePresence initial={false}>
            {sessions.map((s) => {
              const isActive = s.session_id === currentSessionId;
              return (
                <motion.button
                  key={s.session_id}
                  layout
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, height: 0 }}
                  onClick={() => onSelectSession(s.session_id)}
                  className={`w-full group flex items-start gap-2.5 px-2.5 py-2 rounded-lg text-left transition-colors ${
                    isActive
                      ? "bg-indigo-600/10 text-white"
                      : "text-white/50 hover:bg-white/5 hover:text-white/70"
                  }`}
                >
                  <MessageSquare
                    size={14}
                    className="mt-0.5 shrink-0 opacity-40"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm truncate leading-snug">
                      {s.title}
                    </p>
                    <p className="text-[10px] text-white/25 mt-0.5">
                      {formatDate(s.updated_at)}
                    </p>
                  </div>
                  <button
                    onClick={(e) => handleDelete(e, s.session_id)}
                    className="shrink-0 mt-0.5 w-6 h-6 rounded flex items-center justify-center
                      opacity-0 group-hover:opacity-100 text-white/20 hover:text-red-400
                      hover:bg-red-500/10 transition-all"
                    title="Excluir"
                  >
                    <Trash2 size={12} />
                  </button>
                </motion.button>
              );
            })}
          </AnimatePresence>
        )}
      </div>
    </motion.aside>
  );
}
