import type {
  ContractEvidenceRow,
  Evidence,
  InvoiceEvidenceRow,
  StepData,
} from "../api/types";

/** "63382.54" -> "63,382.54" by string, so no float ever touches a money amount. */
export function money(amount: string): string {
  const [whole, cents] = amount.split(".");
  const grouped = whole.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return cents === undefined ? grouped : `${grouped}.${cents}`;
}

const cell = "px-2 py-1 text-left align-top";

function InvoiceTable({
  rows,
  totals,
}: {
  rows: InvoiceEvidenceRow[];
  totals: Record<string, string>;
}) {
  return (
    <table aria-label="Invoices behind this answer" className="w-full text-xs">
      <thead>
        <tr className="border-b border-slate-200 text-slate-600">
          <th className={cell}>Invoice</th>
          <th className={cell}>Vendor</th>
          <th className={cell}>Date</th>
          <th className={`${cell} text-right`}>Total</th>
          <th className={cell}>Source</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr
            key={`${r.vendor}-${r.invoice_number}`}
            className="border-b border-slate-100"
          >
            <td className={cell}>{r.invoice_number}</td>
            <td className={cell}>{r.vendor}</td>
            <td className={cell}>{r.issue_date}</td>
            <td className={`${cell} text-right tabular-nums`}>
              {money(r.total)}
            </td>
            <td className={cell}>
              {r.filename ? `${r.filename} · p. ${r.page ?? 1}` : "-"}
            </td>
          </tr>
        ))}
      </tbody>
      <tfoot>
        {Object.entries(totals).map(([cur, total]) => (
          <tr key={cur} className="font-medium">
            <th scope="row" colSpan={3} className={cell}>
              Total ({cur})
            </th>
            <td className={`${cell} text-right tabular-nums`}>
              {money(total)}
            </td>
            <td className={cell} />
          </tr>
        ))}
      </tfoot>
    </table>
  );
}

function ContractTable({ rows }: { rows: ContractEvidenceRow[] }) {
  return (
    <table aria-label="Contracts behind this answer" className="w-full text-xs">
      <thead>
        <tr className="border-b border-slate-200 text-slate-600">
          <th className={cell}>Vendor</th>
          <th className={cell}>Payment terms</th>
          <th className={cell}>Notice (days)</th>
          <th className={cell}>Renews automatically</th>
          <th className={cell}>Governing law</th>
          <th className={cell}>Source</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr
            key={`${r.vendor}-${r.filename}`}
            className="border-b border-slate-100"
          >
            <td className={cell}>{r.vendor}</td>
            <td className={cell}>
              {r.payment_terms_days != null
                ? `Net ${r.payment_terms_days}`
                : "-"}
            </td>
            <td className={cell}>{r.termination_notice_days ?? "-"}</td>
            <td className={cell}>
              {r.auto_renewal == null ? "-" : r.auto_renewal ? "yes" : "no"}
            </td>
            <td className={cell}>{r.governing_law ?? "-"}</td>
            <td className={cell}>{r.filename ?? "-"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function summary(e: Evidence): string {
  if (e.kind === "contracts")
    return `Evidence: ${e.count} contract${e.count === 1 ? "" : "s"}`;
  const totals = Object.entries(e.totals)
    .map(([cur, t]) => `${cur} ${money(t)}`)
    .join(" + ");
  return `Evidence: ${e.count} invoice${e.count === 1 ? "" : "s"}${totals ? `, ${totals}` : ""}`;
}

/** The rows behind a computed answer, so a reader can add them up and check the sources. Collapsed
 * by default; plain text only (document contents are never rendered as markup). */
export function EvidencePanel({ steps }: { steps: StepData[] }) {
  const shown = steps.filter((s) => s.evidence && s.evidence.rows.length > 0);
  if (shown.length === 0) return null;
  return (
    <>
      {shown.map((s) => {
        const e = s.evidence as Evidence;
        return (
          <details
            key={s.step_no}
            className="mt-2 rounded border border-emerald-200 bg-white text-sm"
          >
            <summary className="cursor-pointer select-none px-3 py-2 font-medium text-emerald-900">
              {summary(e)}
            </summary>
            <div className="space-y-2 overflow-x-auto border-t border-emerald-200 p-3">
              {e.kind === "invoices" ? (
                <InvoiceTable rows={e.rows} totals={e.totals} />
              ) : (
                <ContractTable rows={e.rows} />
              )}
              {e.truncated && (
                <p className="text-xs text-slate-600">
                  Showing the first {e.rows.length} of {e.count}
                  {e.kind === "invoices"
                    ? " invoices. The totals above cover all of them."
                    : " contracts."}
                </p>
              )}
            </div>
          </details>
        );
      })}
    </>
  );
}
