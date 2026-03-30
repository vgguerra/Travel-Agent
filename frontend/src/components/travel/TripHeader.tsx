"use client";

import { TravelState } from "@/types/travel";
import { MapPin, Calendar, Users, BedDouble, ArrowRight } from "lucide-react";

interface Props {
  state: TravelState;
}

function formatDate(d: string | null): string {
  if (!d) return "";
  const [y, m, day] = d.split("-");
  return `${day}/${m}/${y}`;
}

export function TripHeader({ state }: Props) {
  return (
    <div className="flex items-center gap-4 px-4 sm:px-6 py-2.5 bg-white/[0.03] border-b border-white/5 overflow-x-auto text-xs">
      {state.departure_city && state.destination_city && (
        <div className="flex items-center gap-1.5 text-white/70 shrink-0">
          <MapPin size={13} className="text-sky-400" />
          <span className="font-medium text-white/90">{state.departure_city}</span>
          <ArrowRight size={11} className="text-white/30" />
          <span className="font-medium text-white/90">{state.destination_city}</span>
        </div>
      )}

      {state.departure_date && (
        <div className="flex items-center gap-1.5 text-white/70 shrink-0">
          <Calendar size={13} className="text-indigo-400" />
          <span>{formatDate(state.departure_date)}</span>
          {state.return_date && state.return_date !== state.departure_date && (
            <>
              <ArrowRight size={11} className="text-white/30" />
              <span>{formatDate(state.return_date)}</span>
            </>
          )}
        </div>
      )}

      {state.adults && (
        <div className="flex items-center gap-1.5 text-white/70 shrink-0">
          <Users size={13} className="text-emerald-400" />
          <span>{state.adults} {Number(state.adults) === 1 ? "adulto" : "adultos"}</span>
        </div>
      )}

      {state.rooms && (
        <div className="flex items-center gap-1.5 text-white/70 shrink-0">
          <BedDouble size={13} className="text-amber-400" />
          <span>{state.rooms} {state.rooms === 1 ? "quarto" : "quartos"}</span>
        </div>
      )}

      {state.trip_type && (
        <div className="shrink-0 px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-white/50 text-[10px] uppercase tracking-wider">
          {state.trip_type === "IDA_VOLTA" ? "Ida e volta" : "Somente ida"}
        </div>
      )}
    </div>
  );
}
