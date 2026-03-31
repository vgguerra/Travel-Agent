"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plane, Cloud, TreePalm, Hotel, Bot, ArrowRight, Loader2, AtSign, UserRound } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

const FEATURES = [
  { icon: Cloud, label: "Previsao do Tempo", desc: "Clima real do seu destino via OpenWeatherMap" },
  { icon: TreePalm, label: "Roteiro Turistico", desc: "Atracoes e atividades dia a dia via TripAdvisor" },
  { icon: Plane, label: "Passagens Aereas", desc: "Busca de voos com precos atualizados" },
  { icon: Hotel, label: "Hospedagem", desc: "Hoteis com precos reais via Booking.com" },
];

export function AuthPage() {
  const { signIn, signUp } = useAuth();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [identifier, setIdentifier] = useState("");
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    let err: string | null;
    if (mode === "signup") {
      if (!/^[a-zA-Z0-9_]{3,20}$/.test(username)) {
        setError("Username deve ter 3-20 caracteres (letras, numeros e _).");
        setLoading(false);
        return;
      }
      err = await signUp(email, password, name, username);
      if (!err) {
        setSuccess("Conta criada! Verifique seu e-mail para confirmar.");
        setMode("login");
        setLoading(false);
        return;
      }
    } else {
      err = await signIn(identifier, password);
    }

    if (err) setError(translateError(err));
    setLoading(false);
  };

  const switchMode = () => {
    setMode(mode === "login" ? "signup" : "login");
    setError(null);
    setSuccess(null);
  };

  const isLoginEmail = mode === "login" && identifier.includes("@");

  return (
    <div className="h-screen flex bg-[var(--background)] overflow-hidden">
      {/* Left panel — info */}
      <div className="hidden lg:flex flex-col justify-center flex-1 px-12 xl:px-20 relative">
        <div className="absolute inset-0 opacity-20" style={{
          background: "radial-gradient(ellipse 70% 50% at 30% 50%, rgba(99,102,241,0.2) 0%, transparent 70%)",
        }} />

        <div className="relative z-10 max-w-lg">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-11 h-11 rounded-xl bg-indigo-600 flex items-center justify-center">
              <Plane size={20} className="text-white" />
            </div>
            <div>
              <h1 className="text-white font-bold text-xl">Travel Agent IA</h1>
              <p className="text-white/40 text-xs">Sistema multi-agente de planejamento</p>
            </div>
          </div>

          <h2 className="text-3xl xl:text-4xl font-bold text-white leading-tight mb-4">
            Planeje sua viagem com inteligencia artificial
          </h2>
          <p className="text-white/50 text-sm leading-relaxed mb-10 max-w-md">
            Nosso sistema usa multiplos agentes especializados que consultam APIs reais para montar um plano de viagem completo — clima, roteiro, voos e hoteis — tudo em uma conversa.
          </p>

          <div className="grid grid-cols-2 gap-3">
            {FEATURES.map((f) => {
              const Icon = f.icon;
              return (
                <div key={f.label} className="flex gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                  <div className="shrink-0 w-9 h-9 rounded-lg bg-indigo-600/15 flex items-center justify-center">
                    <Icon size={16} className="text-indigo-400" />
                  </div>
                  <div>
                    <p className="text-white/90 text-sm font-medium">{f.label}</p>
                    <p className="text-white/35 text-[11px] leading-snug">{f.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-10 flex items-center gap-2.5 text-white/25 text-xs">
            <Bot size={14} />
            <span>Powered by Ollama + LangGraph + LangChain</span>
          </div>
        </div>
      </div>

      {/* Right panel — auth form */}
      <div className="flex flex-col items-center justify-center w-full lg:w-[440px] xl:w-[480px] px-6 sm:px-10 lg:border-l border-white/5 bg-white/[0.01]">
        {/* Mobile header */}
        <div className="lg:hidden flex items-center gap-2.5 mb-8">
          <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center">
            <Plane size={16} className="text-white" />
          </div>
          <span className="text-white font-semibold">Travel Agent IA</span>
        </div>

        <div className="w-full max-w-sm">
          <AnimatePresence mode="wait">
            <motion.div
              key={mode}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.15 }}
            >
              <h3 className="text-white text-xl font-bold mb-1">
                {mode === "login" ? "Bem-vindo de volta" : "Crie sua conta"}
              </h3>
              <p className="text-white/40 text-sm mb-6">
                {mode === "login"
                  ? "Entre com seu e-mail ou username"
                  : "Comece a planejar suas viagens com IA"}
              </p>

              <form onSubmit={handleSubmit} className="space-y-3">
                {mode === "signup" && (
                  <>
                    <input
                      type="text"
                      placeholder="Seu nome"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      required
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-white/25 outline-none focus:border-indigo-500/50 transition-colors"
                    />
                    <div className="relative">
                      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-white/20">
                        <AtSign size={15} />
                      </span>
                      <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value.replace(/[^a-zA-Z0-9_]/g, ""))}
                        required
                        maxLength={20}
                        className="w-full bg-white/5 border border-white/10 rounded-xl pl-9 pr-4 py-2.5 text-sm text-white placeholder-white/25 outline-none focus:border-indigo-500/50 transition-colors"
                      />
                    </div>
                    <input
                      type="email"
                      placeholder="E-mail"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-white/25 outline-none focus:border-indigo-500/50 transition-colors"
                    />
                  </>
                )}

                {mode === "login" && (
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-white/20">
                      {isLoginEmail ? <AtSign size={15} /> : <UserRound size={15} />}
                    </span>
                    <input
                      type="text"
                      placeholder="E-mail ou username"
                      value={identifier}
                      onChange={(e) => setIdentifier(e.target.value)}
                      required
                      className="w-full bg-white/5 border border-white/10 rounded-xl pl-9 pr-4 py-2.5 text-sm text-white placeholder-white/25 outline-none focus:border-indigo-500/50 transition-colors"
                    />
                  </div>
                )}

                <input
                  type="password"
                  placeholder="Senha"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-white/25 outline-none focus:border-indigo-500/50 transition-colors"
                />

                {error && (
                  <p className="text-red-400 text-xs bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
                    {error}
                  </p>
                )}
                {success && (
                  <p className="text-emerald-400 text-xs bg-emerald-500/10 border border-emerald-500/20 rounded-lg px-3 py-2">
                    {success}
                  </p>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium text-sm rounded-xl px-4 py-2.5 transition-colors"
                >
                  {loading ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <>
                      {mode === "login" ? "Entrar" : "Criar conta"}
                      <ArrowRight size={15} />
                    </>
                  )}
                </button>
              </form>

              <p className="text-center text-white/30 text-xs mt-5">
                {mode === "login" ? "Ainda nao tem conta?" : "Ja tem conta?"}{" "}
                <button onClick={switchMode} className="text-indigo-400 hover:text-indigo-300 transition-colors">
                  {mode === "login" ? "Criar conta" : "Fazer login"}
                </button>
              </p>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

function translateError(msg: string): string {
  if (msg.includes("Invalid login")) return "E-mail/username ou senha incorretos.";
  if (msg.includes("already registered")) return "Este e-mail ja esta cadastrado.";
  if (msg.includes("Password should be")) return "A senha deve ter pelo menos 6 caracteres.";
  if (msg.includes("valid email")) return "Digite um e-mail valido.";
  if (msg.includes("Email not confirmed")) return "Confirme seu e-mail antes de fazer login.";
  if (msg.includes("username")) return msg;
  if (msg.includes("Usuario")) return msg;
  return msg;
}
