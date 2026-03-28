"use client";

const SUGGESTIONS = [
  "Quero viajar de São Paulo para Florianópolis em julho",
  "Planeje uma viagem de Curitiba para Rio de Janeiro para 2 adultos",
  "Voo de ida e volta de Brasília para Recife, 3 pessoas",
  "Preciso de hotel em Gramado para o feriado de novembro",
];

interface Props {
  onSelect: (text: string) => void;
}

export function ChatSuggestions({ onSelect }: Props) {
  return (
    <div className="space-y-2">
      <p className="text-white/30 text-xs text-center">Sugestões para começar</p>
      <div className="grid grid-cols-1 gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => onSelect(s)}
            className="text-left text-sm text-white/60 hover:text-white px-4 py-2.5 rounded-xl
              border border-white/10 hover:border-sky-500/50 hover:bg-sky-500/5
              transition-all duration-200 leading-snug"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
