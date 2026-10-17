import { useQueryClient } from "@tanstack/react-query";
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { setUnauthorizedHandler, tokenStore } from "./api/client";

interface AuthValue {
  token: string | null;
  signIn: (token: string) => void;
  signOut: () => void;
}

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => tokenStore.get());
  const queryClient = useQueryClient();

  const signOut = useCallback(() => {
    tokenStore.clear();
    setToken(null);
    queryClient.clear(); // never show the previous user's documents to the next one
  }, [queryClient]);

  const signIn = useCallback((t: string) => {
    tokenStore.set(t);
    setToken(t);
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(signOut); // any 401 from the API ends the session
    return () => setUnauthorizedHandler(null);
  }, [signOut]);

  const value = useMemo(() => ({ token, signIn, signOut }), [token, signIn, signOut]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}

export function RequireAuth({ children }: { children: ReactNode }) {
  const { token } = useAuth();
  const location = useLocation();
  if (!token) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return <>{children}</>;
}
