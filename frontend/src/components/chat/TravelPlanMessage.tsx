"use client";

import { TravelState } from "@/types/travel";
import { Cloud, TreePalm, Plane, Hotel, LucideIcon } from "lucide-react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Props {
  reply: string;
  state: TravelState;
}

interface SectionConfig {
  key: keyof TravelState;
  label: string;
  icon: LucideIcon;
  accent: string;
  border: string;
  bg: string;
  iconBg: string;
}

const SECTIONS: SectionConfig[] = [
  {
    key: "weather",
    label: "Clima",
    icon: Cloud,
    accent: "text-cyan-400",
    border: "border-cyan-500/15",
    bg: "bg-cyan-500/[0.04]",
    iconBg: "bg-cyan-500/10",
  },
  {
    key: "tourism",
    label: "Roteiro & Atrações",
    icon: TreePalm,
    accent: "text-emerald-400",
    border: "border-emerald-500/15",
    bg: "bg-emerald-500/[0.04]",
    iconBg: "bg-emerald-500/10",
  },
  {
    key: "transport",
    label: "Transporte",
    icon: Plane,
    accent: "text-violet-400",
    border: "border-violet-500/15",
    bg: "bg-violet-500/[0.04]",
    iconBg: "bg-violet-500/10",
  },
  {
    key: "accommodation",
    label: "Hospedagem",
    icon: Hotel,
    accent: "text-amber-400",
    border: "border-amber-500/15",
    bg: "bg-amber-500/[0.04]",
    iconBg: "bg-amber-500/10",
  },
];

function SectionCard({ config, content, index }: { config: SectionConfig; content: string; index: number }) {
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: index * 0.08 }}
      className={`rounded-xl border ${config.border} ${config.bg} overflow-hidden`}
    >
      <div className="flex items-center gap-2 px-4 py-2.5 border-b border-white/5">
        <div className={`w-6 h-6 rounded-md ${config.iconBg} flex items-center justify-center`}>
          <Icon size={13} className={config.accent} />
        </div>
        <span className={`text-xs font-semibold uppercase tracking-wider ${config.accent}`}>
          {config.label}
        </span>
      </div>
      <div className="px-4 py-3">
        <div className="prose-chat text-[13px] leading-relaxed">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
        </div>
      </div>
    </motion.div>
  );
}

export function TravelPlanMessage({ reply, state }: Props) {
  const activeSections = SECTIONS.filter((s) => {
    const val = state[s.key];
    return val && typeof val === "string" && val.trim().length > 0;
  });

  return (
    <div className="space-y-3">
      {/* Summary / reply from conversational agent */}
      {reply.trim().length > 0 && (
        <div className="prose-chat text-[14px]">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{reply}</ReactMarkdown>
        </div>
      )}

      {/* Agent result cards */}
      {activeSections.length > 0 && (
        <div className="space-y-2.5 pt-1">
          {activeSections.map((section, i) => (
            <SectionCard
              key={section.key}
              config={section}
              content={state[section.key] as string}
              index={i}
            />
          ))}
        </div>
      )}
    </div>
  );
}
