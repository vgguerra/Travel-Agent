"use client";

import { motion } from "framer-motion";
import { Bot } from "lucide-react";

export function TypingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="shrink-0 w-8 h-8 rounded-lg bg-indigo-600/80 text-white flex items-center justify-center">
        <Bot size={16} />
      </div>
      <div className="bg-white/4 border border-white/6 rounded-2xl rounded-tl-md px-4 py-3 flex items-center gap-1.5">
        <span className="text-white/30 text-xs mr-1">Planejando</span>
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-indigo-400/70"
            animate={{ opacity: [0.3, 1, 0.3] }}
            transition={{
              duration: 1,
              repeat: Infinity,
              delay: i * 0.2,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>
    </div>
  );
}
