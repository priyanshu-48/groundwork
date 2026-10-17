import { useQuery } from "@tanstack/react-query";
import { NavLink, Outlet } from "react-router-dom";
import { getMeta } from "../api/client";
import { useAuth } from "../auth";
import { useIsDemo } from "../useIsDemo";

const link = ({ isActive }: { isActive: boolean }) =>
  `rounded px-3 py-1.5 text-sm font-medium ${isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-200"}`;

export function Layout() {
  const { signOut } = useAuth();
  const meta = useQuery({ queryKey: ["meta"], queryFn: getMeta, staleTime: 60_000 });
  const isDemo = useIsDemo();
  return (
    <div className="flex h-screen flex-col">
      <header className="flex items-center gap-4 border-b border-slate-200 bg-white px-4 py-2">
        <span className="text-lg font-semibold">Groundwork</span>
        <nav className="flex gap-1" aria-label="Main">
          <NavLink to="/documents" className={link}>
            Documents
          </NavLink>
          <NavLink to="/chat" className={link}>
            Chat
          </NavLink>
        </nav>
        <button type="button" onClick={signOut} className="ml-auto text-sm text-slate-600 underline">
          Sign out
        </button>
      </header>
      {isDemo && (
        <p role="status" className="bg-indigo-100 px-4 py-1.5 text-sm text-indigo-900">
          Shared demo workspace with synthetic data. It is read-only, and your questions are private to
          this session.
        </p>
      )}
      {meta.data?.chat === "demo" && (
        <p role="status" className="bg-amber-100 px-4 py-1.5 text-sm text-amber-900">
          Demo mode: answers come from a simple document lookup, not a language model.
        </p>
      )}
      {meta.data?.chat === "unavailable" && (
        <p role="status" className="bg-red-100 px-4 py-1.5 text-sm text-red-900">
          Chat is not configured on this server. You can still upload and browse documents.
        </p>
      )}
      <main className="min-h-0 flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
