"use client";

import { TravelState } from "@/types/travel";
import {
  MapPin,
  Calendar,
  Users,
  BedDouble,
  Repeat2,
  ArrowRight,
} from "lucide-react";

interface Props {
  state: TravelState;
}

function Field({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | null | number;
}) {
  if (!value) return null;
  return (
    <div className="flex items-start gap-2.5">
      <span className="text-sky-400 mt-0.5 flex-shrink-0">{icon}</span>
      <div>
        <p className="text-white/40 text-[10px] uppercase tracking-wider">{label}</p>
        <p className="text-white text-sm font-medium">{value}</p>
      </div>
    </div>
  );
}

export function TripSummaryCard({ state }: Props) {
  const hasAnyField = Object.values(state).some((v) => v !== null);
  if (!hasAnyField) return null;

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm p-5 space-y-4">
      <h3 className="text-white/60 text-xs font-semibold uppercase tracking-widest">
        Resumo da Viagem
      </h3>

      <div className="grid grid-cols-1 gap-3">
        {state.departure_city && state.destination_city ? (
          <div className="flex items-center gap-2">
            <span className="text-sky-400">
              <MapPin size={15} />
            </span>
            <p className="text-white text-sm font-medium">
              {state.departure_city}
              <ArrowRight size={13} className="inline mx-1 text-white/40" />
              {state.destination_city}
            </p>
          </div>
        ) : (
          <>
            <Field icon={<MapPin size={15} />} label="Origem" value={state.departure_city} />
            <Field icon={<MapPin size={15} />} label="Destino" value={state.destination_city} />
          </>
        )}

        {state.departure_date && state.return_date ? (
          <div className="flex items-center gap-2">
            <span className="text-sky-400">
              <Calendar size={15} />
            </span>
            <p className="text-white text-sm font-medium">
              {state.departure_date}
              <ArrowRight size={13} className="inline mx-1 text-white/40" />
              {state.return_date}
            </p>
          </div>
        ) : (
          <>
            <Field icon={<Calendar size={15} />} label="Ida" value={state.departure_date} />
            <Field icon={<Calendar size={15} />} label="Volta" value={state.return_date} />
          </>
        )}

        <Field icon={<Users size={15} />} label="Adultos" value={state.adults} />
        <Field icon={<BedDouble size={15} />} label="Quartos" value={state.rooms} />
        <Field icon={<Repeat2 size={15} />} label="Tipo" value={state.trip_type} />
      </div>
    </div>
  );
}
