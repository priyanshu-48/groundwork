import type { Citation } from "../api/types";

export type Segment = { kind: "text"; value: string } | { kind: "refs"; refs: string[] };

const MARKER = /\[(C\d+(?:\s*,\s*C\d+)*)\]/g;

/** Split an answer into plain text and citation markers such as [C1] or [C1, C2]. */
export function splitCitations(text: string): Segment[] {
  const out: Segment[] = [];
  let last = 0;
  for (const m of text.matchAll(MARKER)) {
    if (m.index > last) out.push({ kind: "text", value: text.slice(last, m.index) });
    out.push({ kind: "refs", refs: m[1]!.split(/\s*,\s*/) });
    last = m.index + m[0].length;
  }
  if (last < text.length) out.push({ kind: "text", value: text.slice(last) });
  return out;
}

interface Props {
  text: string;
  citations: Citation[];
  selected: string | null;
  onSelect: (ref: string | null) => void;
}

/**
 * Renders the answer as plain text (never HTML) with known citation markers turned into buttons.
 * A marker the server did not send a citation for stays as ordinary text.
 */
export function CitedText({ text, citations, selected, onSelect }: Props) {
  const byRef = new Map(citations.map((c) => [c.ref, c]));
  return (
    <span className="whitespace-pre-wrap">
      {splitCitations(text).map((seg, i) =>
        seg.kind === "text" ? (
          <span key={i}>{seg.value}</span>
        ) : (
          <span key={i}>
            {seg.refs.map((ref, j) => {
              const c = byRef.get(ref);
              if (!c) return <span key={j}>[{ref}]</span>;
              const open = selected === ref;
              return (
                <button
                  key={j}
                  type="button"
                  aria-expanded={open}
                  aria-label={`Source ${ref}: ${c.filename}, page ${c.page}`}
                  onClick={() => onSelect(open ? null : ref)}
                  className="mx-0.5 inline-flex items-center rounded bg-indigo-50 px-1.5 text-xs font-semibold text-indigo-700 ring-1 ring-inset ring-indigo-300 hover:bg-indigo-100 focus:outline-2 focus:outline-indigo-500"
                >
                  {ref}
                </button>
              );
            })}
          </span>
        ),
      )}
    </span>
  );
}
