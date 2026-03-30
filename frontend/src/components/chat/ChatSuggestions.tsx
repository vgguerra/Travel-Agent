"use client";

import { MapPin, Users, Plane, Calendar } from "lucide-react";

const SUGGESTIONS = [
  {
    icon: Plane,
    text: "Quero ir de SP para Florianópolis, 10 a 17 de julho, 2 adultos, 1 quarto",
  },
  {
    icon: Users,
    text: "Viagem em família de Curitiba para Rio de Janeiro, 3 adultos, 2 quartos, ida e volta em agosto",
  },
  {
    icon: MapPin,
    text: "Viagem de Brasília para Salvador, saindo dia 05/05 e voltando 12/05",
  },
  {
    icon: Calendar,
    text: "Quero viajar de Porto Alegre para Recife no feriado de novembro, 1 adulto",
  },
];

interface Props {
  onSelect: (text: string) => void;
}

export function ChatSuggestions({ onSelect }: Props) {
  return (
    <div className="w-full max-w-lg mx-auto">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {SUGGESTIONS.map((s) => {
          const Icon = s.icon;
          return (
            <button
              key={s.text}
              onClick={() => onSelect(s.text)}
              className="group text-left text-[13px] text-white/50 hover:text-white/80
                px-3.5 py-3 rounded-xl border border-white/6 hover:border-white/12
                hover:bg-white/[0.03] transition-all duration-200 leading-snug flex gap-2.5"
            >
              <Icon size={15} className="shrink-0 mt-0.5 text-white/20 group-hover:text-indigo-400 transition-colors" />
              <span>{s.text}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
