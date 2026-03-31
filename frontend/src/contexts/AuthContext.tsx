"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { User, Session } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabase";

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
    // Check if username is already taken
    const { data: existing } = await supabase
      .from("profiles")
      .select("id")
      .eq("username", username.toLowerCase())
      .single();

    if (existing) return "Este username ja esta em uso.";

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

    // If it doesn't look like an email, treat as username
    if (!identifier.includes("@")) {
      const { data: profile, error } = await supabase
        .from("profiles")
        .select("email")
        .eq("username", identifier.toLowerCase())
        .single();

      if (error || !profile) return "Usuario nao encontrado.";
      email = profile.email;
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
