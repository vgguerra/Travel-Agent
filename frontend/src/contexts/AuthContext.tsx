"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
} from "react";
import {
  signUp as apiSignUp,
  signIn as apiSignIn,
  signOut as apiSignOut,
  loadTokens,
  getAccessToken,
  AuthUser,
} from "@/lib/api";

interface AuthState {
  user: AuthUser | null;
  loading: boolean;
  signUp: (email: string, password: string, name: string, username: string) => Promise<string | null>;
  signIn: (identifier: string, password: string) => Promise<string | null>;
  signOut: () => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

function restoreUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  loadTokens();
  if (!getAccessToken()) return null;
  try {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(restoreUser);
  const loading = false;

  const signUp = useCallback(
    async (
      email: string,
      password: string,
      name: string,
      username: string,
    ): Promise<string | null> => {
      try {
        const data = await apiSignUp(email, password, name, username);
        if (data.user) setUser(data.user);
        return null;
      } catch (err) {
        return err instanceof Error ? err.message : "Erro ao criar conta.";
      }
    },
    [],
  );

  const signIn = useCallback(
    async (identifier: string, password: string): Promise<string | null> => {
      try {
        const data = await apiSignIn(identifier, password);
        setUser(data.user);
        return null;
      } catch (err) {
        return err instanceof Error ? err.message : "Erro ao entrar.";
      }
    },
    [],
  );

  const signOut = useCallback(() => {
    apiSignOut();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, signUp, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
