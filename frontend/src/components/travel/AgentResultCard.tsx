"use client";

import { motion } from "framer-motion";
import { Cloud, TreePalm, Plane, Hotel, LucideIcon } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Props {
  type: "weather" | "tourism" | "transport" | "accommodation";
  content: string;
}

const CONFIG: Record<
  Props["type"],
  { label: string; icon: LucideIcon; color: string; bg: string }
> = {
  weather: {
    label: "Previsão do Tempo",
    icon: Cloud,
    color: "text-cyan-400",
    bg: "border-cyan-500/30 bg-cyan-950/30",
  },
  tourism: {
    label: "Turismo & Atrações",
    icon: TreePalm,
    color: "text-emerald-400",
    bg: "border-emerald-500/30 bg-emerald-950/30",
  },
  transport: {
    label: "Voos & Transporte",
    icon: Plane,
    color: "text-violet-400",
    bg: "border-violet-500/30 bg-violet-950/30",
  },
  accommodation: {
    label: "Hospedagem",
    icon: Hotel,
    color: "text-amber-400",
    bg: "border-amber-500/30 bg-amber-950/30",
  },
};

export function AgentResultCard({ type, content }: Props) {
  const cfg = CONFIG[type];
  const Icon = cfg.icon;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className={`rounded-2xl border backdrop-blur-sm p-4 space-y-2 ${cfg.bg}`}
    >
      <div className={`flex items-center gap-2 ${cfg.color}`}>
        <Icon size={16} />
        <span className="text-xs font-semibold uppercase tracking-wider">
          {cfg.label}
        </span>
      </div>
      <div className="prose-chat text-white/80 text-sm">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {content}
        </ReactMarkdown>
      </div>
    </motion.div>
  );
}
