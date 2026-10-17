import type { StepData } from "../api/types";

const LABEL = { running: "running", ok: "done", error: "failed" } as const;

/** What the agent did, tool by tool. Collapsed by default so the answer stays the focus. */
export function StepsPanel({ steps }: { steps: StepData[] }) {
  if (steps.length === 0) return null;
  return (
    <details className="mt-2 rounded border border-slate-200 bg-white text-sm">
      <summary className="cursor-pointer select-none px-3 py-2 font-medium text-slate-700">
        Steps ({steps.length})
      </summary>
      <ol className="space-y-2 border-t border-slate-200 p-3">
        {steps.map((s) => (
          <li key={s.step_no}>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-semibold">{s.tool}</span>
              <span className={s.status === "error" ? "text-red-700" : "text-slate-500"}>
                {LABEL[s.status]}
                {s.latency_ms !== undefined ? ` · ${s.latency_ms} ms` : ""}
              </span>
            </div>
            <pre className="mt-1 overflow-x-auto rounded bg-slate-50 p-2 text-xs">{JSON.stringify(s.args)}</pre>
            {s.preview && <p className="mt-1 text-xs text-slate-600">{s.preview}</p>}
          </li>
        ))}
      </ol>
    </details>
  );
}
