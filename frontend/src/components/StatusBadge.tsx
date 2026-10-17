import type { DocStatus } from "../api/types";

const STYLES: Record<DocStatus, string> = {
  pending: "bg-slate-100 text-slate-700 ring-slate-300",
  processing: "bg-amber-50 text-amber-800 ring-amber-300",
  ready: "bg-emerald-50 text-emerald-800 ring-emerald-300",
  failed: "bg-red-50 text-red-800 ring-red-300",
};

/** The label is text, so status never depends on colour alone. */
export function StatusBadge({ status }: { status: DocStatus }) {
  return (
    <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${STYLES[status]}`}>
      {status}
    </span>
  );
}
