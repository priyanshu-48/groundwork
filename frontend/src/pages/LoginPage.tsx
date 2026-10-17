import { useMutation } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { login, signup } from "../api/client";
import { useAuth } from "../auth";

export function LoginPage() {
  const { token, signIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: string } | null)?.from ?? "/documents";
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [orgName, setOrgName] = useState("");

  const auth = useMutation({
    mutationFn: () => (mode === "login" ? login(email, password) : signup(orgName, email, password)),
    onSuccess: (t) => {
      signIn(t);
      navigate(from, { replace: true });
    },
  });

  if (token) return <Navigate to={from} replace />;

  const submit = (e: FormEvent) => {
    e.preventDefault();
    auth.mutate();
  };

  const field = "mt-1 w-full rounded border border-slate-300 px-3 py-2 focus:outline-2 focus:outline-indigo-500";
  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <form onSubmit={submit} className="w-full max-w-sm space-y-4 rounded-lg bg-white p-6 shadow">
        <h1 className="text-xl font-semibold">{mode === "login" ? "Sign in to Groundwork" : "Create your workspace"}</h1>
        {mode === "signup" && (
          <label className="block text-sm font-medium">
            Company name
            <input className={field} value={orgName} onChange={(e) => setOrgName(e.target.value)} required maxLength={100} />
          </label>
        )}
        <label className="block text-sm font-medium">
          Email
          <input className={field} type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label className="block text-sm font-medium">
          Password
          <input
            className={field}
            type="password"
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={mode === "signup" ? 10 : undefined}
          />
          {mode === "signup" && <span className="text-xs font-normal text-slate-500">At least 10 characters.</span>}
        </label>
        {auth.error && (
          <p role="alert" className="text-sm text-red-700">
            {auth.error.message}
          </p>
        )}
        <button
          type="submit"
          disabled={auth.isPending}
          className="w-full rounded bg-slate-900 py-2 font-medium text-white disabled:opacity-60"
        >
          {auth.isPending ? "Please wait..." : mode === "login" ? "Sign in" : "Create account"}
        </button>
        <button
          type="button"
          className="w-full text-sm text-slate-600 underline"
          onClick={() => {
            auth.reset();
            setMode(mode === "login" ? "signup" : "login");
          }}
        >
          {mode === "login" ? "New here? Create a workspace" : "Already have an account? Sign in"}
        </button>
      </form>
    </div>
  );
}
