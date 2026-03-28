"use client";

import { TravelState } from "@/types/travel";
import { TripSummaryCard } from "./TripSummaryCard";
import { AgentResultCard } from "./AgentResultCard";
import { motion, AnimatePresence } from "framer-motion";

interface Props {
  state: TravelState | null;
}

export function TravelInfoPanel({ state }: Props) {
  if (!state) return null;

  const results = [
    state.weather && { type: "weather" as const, content: state.weather },
    state.tourism && { type: "tourism" as const, content: state.tourism },
    state.transport && { type: "transport" as const, content: state.transport },
    state.accommodation && {
      type: "accommodation" as const,
      content: state.accommodation,
    },
  ].filter(Boolean) as { type: "weather" | "tourism" | "transport" | "accommodation"; content: string }[];

  return (
    <div className="space-y-4">
      <TripSummaryCard state={state} />

      <AnimatePresence>
        {results.map((r) => (
          <AgentResultCard key={r.type} type={r.type} content={r.content} />
        ))}
      </AnimatePresence>
    </div>
  );
}
