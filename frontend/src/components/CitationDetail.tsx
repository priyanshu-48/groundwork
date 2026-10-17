import type { Citation } from "../api/types";

export function CitationDetail({ citation, onClose }: { citation: Citation; onClose: () => void }) {
  return (
    <aside
      aria-label={`Source ${citation.ref}`}
      className="mt-2 rounded border border-indigo-200 bg-indigo-50 p-3 text-sm"
    >
      <div className="flex items-start justify-between gap-2">
        <p className="font-medium text-indigo-900">
          {citation.filename} <span className="font-normal">· page {citation.page}</span>
        </p>
        <button type="button" onClick={onClose} className="text-xs text-indigo-700 underline">
          Close
        </button>
      </div>
      <p className="mt-1 whitespace-pre-wrap text-slate-700">{citation.snippet}</p>
    </aside>
  );
}
