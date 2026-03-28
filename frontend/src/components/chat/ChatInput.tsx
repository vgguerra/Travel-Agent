"use client";

import { useState, KeyboardEvent, useRef, useEffect } from "react";
import { SendHorizonal } from "lucide-react";

interface Props {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [value]);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex items-end gap-2 bg-white/5 border border-white/10 rounded-2xl px-4 py-3 backdrop-blur-sm">
      <textarea
        ref={textareaRef}
        rows={1}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder="Ex: Quero ir de São Paulo para Florianópolis em 15/07…"
        className="flex-1 bg-transparent resize-none text-white placeholder-white/30 text-sm outline-none leading-relaxed disabled:opacity-50"
      />
      <button
        onClick={handleSend}
        disabled={disabled || !value.trim()}
        aria-label="Enviar mensagem"
        className="flex-shrink-0 w-9 h-9 rounded-xl bg-sky-500 hover:bg-sky-400 disabled:opacity-40
          disabled:cursor-not-allowed text-white flex items-center justify-center transition-colors"
      >
        <SendHorizonal size={16} />
      </button>
    </div>
  );
}
