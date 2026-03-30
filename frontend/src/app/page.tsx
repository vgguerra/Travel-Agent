"use client";

import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plane, RotateCcw } from "lucide-react";

import { useChat } from "@/hooks/useChat";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { TypingIndicator } from "@/components/chat/TypingIndicator";
import { ChatInput } from "@/components/chat/ChatInput";
import { ChatSuggestions } from "@/components/chat/ChatSuggestions";
import { TripHeader } from "@/components/travel/TripHeader";

export default function Home() {
  const { messages, loading, error, travelState, send, reset } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const isEmpty = messages.length === 0;
  const hasTrip = travelState && travelState.departure_city && travelState.destination_city;

  return (
    <div className="h-screen flex flex-col bg-[var(--background)]">
      {/* Header */}
      <header className="flex-shrink-0 flex items-center justify-between px-4 sm:px-6 h-14 border-b border-white/5 bg-[var(--background)]/80 backdrop-blur-md z-20">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
            <Plane size={15} className="text-white" />
          </div>
          <span className="text-white font-semibold text-sm">Travel Agent</span>
          <span className="text-white/25 text-sm font-light hidden sm:inline">|</span>
          <span className="text-white/35 text-xs hidden sm:inline">Assistente de viagem</span>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-2.5 py-0.5">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-emerald-400 text-[11px] font-medium">Online</span>
          </div>
          {!isEmpty && (
            <button
              onClick={reset}
              title="Nova conversa"
              className="w-8 h-8 rounded-lg flex items-center justify-center text-white/30
                hover:text-white hover:bg-white/5 transition-colors"
            >
              <RotateCcw size={14} />
            </button>
          )}
        </div>
      </header>

      {/* Trip summary bar */}
      <AnimatePresence>
        {hasTrip && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="flex-shrink-0 overflow-hidden z-10"
          >
            <TripHeader state={travelState} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6">
          <AnimatePresence initial={false}>
            {isEmpty ? (
              <motion.div
                key="welcome"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center pt-[12vh] pb-8 space-y-10"
              >
                <div className="text-center space-y-3">
                  <div className="w-14 h-14 rounded-2xl bg-indigo-600/20 border border-indigo-500/20 flex items-center justify-center mx-auto mb-4">
                    <Plane size={24} className="text-indigo-400" />
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
                    Para onde vamos?
                  </h2>
                  <p className="text-white/40 text-sm max-w-sm mx-auto leading-relaxed">
                    Me conte os detalhes da sua viagem e eu preparo um plano completo com clima, atrações, voos e hospedagem.
                  </p>
                </div>
                <ChatSuggestions onSelect={send} />
              </motion.div>
            ) : (
              <div className="space-y-5">
                {messages.map((msg) => (
                  <MessageBubble key={msg.id} message={msg} />
                ))}
              </div>
            )}
          </AnimatePresence>

          {loading && (
            <div className="mt-5">
              <TypingIndicator />
            </div>
          )}

          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-4 rounded-xl border border-red-500/20 bg-red-950/20 text-red-300 text-sm px-4 py-3"
            >
              {error}
            </motion.div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input */}
      <div className="flex-shrink-0 border-t border-white/5 bg-[var(--background)]/80 backdrop-blur-md">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-3">
          <ChatInput onSend={send} disabled={loading} />
        </div>
      </div>
    </div>
  );
}
