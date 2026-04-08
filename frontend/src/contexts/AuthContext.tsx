"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { User, Session } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabase";
import { checkUsername, resolveUsername } from "@/lib/api";

interface AuthState {
  user: User | null;
  session: Session | null;
  loading: boolean;
  signUp: (email: string, password: string, name: string, username: string) => Promise<string | null>;
  signIn: (identifier: string, password: string) => Promise<string | null>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const signUp = async (
    email: string,
    password: string,
    name: string,
    username: string,
  ): Promise<string | null> => {
    // Check username via backend
    try {
      const { exists } = await checkUsername(username);
      if (exists) return "Este username ja esta em uso.";
    } catch {
      return "Erro ao verificar username.";
    }

    // Create auth user — the DB trigger handle_new_user() auto-creates the profile row
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { name, username: username.toLowerCase() } },
    });

    return error?.message ?? null;
  };

  const signIn = async (identifier: string, password: string): Promise<string | null> => {
    let email = identifier;

    // If it doesn't look like an email, resolve username via backend
    if (!identifier.includes("@")) {
      try {
        const result = await resolveUsername(identifier);
        email = result.email;
      } catch {
        return "Usuario nao encontrado.";
      }
    }

    const { error } = await supabase.auth.signInWithPassword({ email, password });
    return error?.message ?? null;
  };

  const signOut = async () => {
    await supabase.auth.signOut();
  };

  return (
    <AuthContext.Provider value={{ user, session, loading, signUp, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
