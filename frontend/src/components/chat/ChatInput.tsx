"use client";

import { useState, KeyboardEvent, useRef, useEffect } from "react";
import { ArrowUp } from "lucide-react";

interface Props {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 140)}px`;
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
    <div className="relative flex items-end gap-2 bg-white/5 border border-white/8 rounded-xl px-3 py-2.5 focus-within:border-white/15 transition-colors">
      <textarea
        ref={textareaRef}
        rows={1}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder="Descreva sua viagem..."
        className="flex-1 bg-transparent resize-none text-white placeholder-white/25 text-sm outline-none leading-relaxed disabled:opacity-40"
      />
      <button
        onClick={handleSend}
        disabled={disabled || !value.trim()}
        aria-label="Enviar mensagem"
        className="shrink-0 w-8 h-8 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30
          disabled:cursor-not-allowed text-white flex items-center justify-center transition-colors"
      >
        <ArrowUp size={16} strokeWidth={2.5} />
      </button>
    </div>
  );
}
