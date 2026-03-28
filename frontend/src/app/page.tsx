"use client";

import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plane, RotateCcw, Sparkles } from "lucide-react";

import { useChat } from "@/hooks/useChat";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { TypingIndicator } from "@/components/chat/TypingIndicator";
import { ChatInput } from "@/components/chat/ChatInput";
import { ChatSuggestions } from "@/components/chat/ChatSuggestions";
import { TravelInfoPanel } from "@/components/travel/TravelInfoPanel";

export default function Home() {
  const { messages, loading, error, travelState, send, reset } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const isEmpty = messages.length === 0;

  return (
    <div
      className="h-screen flex flex-col overflow-hidden"
      style={{
        background: "linear-gradient(135deg, #0a0f1e 0%, #0d1830 50%, #0a1628 100%)",
      }}
    >
      {/* Subtle ambient glow */}
      <div
        className="pointer-events-none absolute inset-0 opacity-30"
        style={{
          background:
            "radial-gradient(ellipse 80% 60% at 50% 0%, rgba(99,102,241,0.15) 0%, transparent 70%)",
        }}
      />

      {/* Header */}
      <header className="relative z-10 flex items-center justify-between px-6 py-4 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-900/50">
            <Plane size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-white font-semibold text-base leading-tight">Travel Agent IA</h1>
            <p className="text-white/40 text-xs">Assistente de viagem multi-agente</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-3 py-1">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-emerald-400 text-xs font-medium">Local LLM</span>
          </div>

          {!isEmpty && (
            <button
              onClick={reset}
              title="Nova conversa"
              className="w-8 h-8 rounded-xl flex items-center justify-center text-white/40
                hover:text-white hover:bg-white/5 transition-colors"
            >
              <RotateCcw size={15} />
            </button>
          )}
        </div>
      </header>

      {/* Main layout */}
      <div className="relative z-10 flex flex-1 overflow-hidden">
        {/* Chat column */}
        <div className="flex flex-col flex-1 min-w-0">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-4">
            <AnimatePresence initial={false}>
              {isEmpty ? (
                <motion.div
                  key="welcome"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="flex flex-col items-center justify-center h-full pt-16 pb-8 space-y-8"
                >
                  {/* Hero */}
                  <div className="text-center space-y-3">
                    <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 rounded-full px-4 py-1.5 mb-2">
                      <Sparkles size={13} className="text-indigo-400" />
                      <span className="text-indigo-300 text-xs font-medium">
                        Multi-Agent AI System
                      </span>
                    </div>
                    <h2 className="text-3xl font-bold text-white tracking-tight">
                      Planeje sua viagem
                    </h2>
                    <p className="text-white/40 text-sm max-w-xs">
                      Clima, voos, hotéis e atrações — tudo em uma conversa.
                    </p>
                  </div>

                  {/* Suggestions */}
                  <div className="w-full max-w-lg">
                    <ChatSuggestions onSelect={send} />
                  </div>
                </motion.div>
              ) : (
                messages.map((msg) => (
                  <MessageBubble key={msg.id} message={msg} />
                ))
              )}
            </AnimatePresence>

            {loading && <TypingIndicator />}

            {error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="rounded-xl border border-red-500/30 bg-red-950/30 text-red-300 text-sm px-4 py-3"
              >
                {error}
              </motion.div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="px-4 md:px-8 pb-6 pt-2">
            <ChatInput onSend={send} disabled={loading} />
            <p className="text-center text-white/20 text-[10px] mt-2">
              Pressione Enter para enviar · Shift+Enter para nova linha
            </p>
          </div>
        </div>

        {/* Sidebar — travel info (desktop) */}
        {travelState && (
          <motion.aside
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
            className="hidden lg:block w-80 xl:w-96 border-l border-white/5 overflow-y-auto p-5"
          >
            <TravelInfoPanel state={travelState} />
          </motion.aside>
        )}
      </div>
    </div>
  );
}
