import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import type { Evidence, StepData } from "../api/types";
import { EvidencePanel } from "./EvidencePanel";

const invoices: Evidence = {
  kind: "invoices",
  rows: [
    {
      invoice_number: "A-1",
      vendor: "Acme Corp",
      issue_date: "2025-03-01",
      currency: "USD",
      total: "30000.10",
      filename: "invoice_A-1.pdf",
      page: 1,
    },
    {
      invoice_number: "A-2",
      vendor: "Acme Corp",
      issue_date: "2025-03-31",
      currency: "USD",
      total: "33382.44",
      filename: "invoice_A-2.pdf",
      page: 1,
    },
  ],
  totals: { USD: "63382.54" },
  count: 2,
  truncated: false,
};

const step = (evidence?: Evidence, over: Partial<StepData> = {}): StepData => ({
  step_no: 1,
  tool: "query_invoices",
  args: {},
  status: "ok",
  evidence,
  ...over,
});

describe("EvidencePanel", () => {
  it("summarises the rows and the total, then lists every invoice with its source", async () => {
    render(<EvidencePanel steps={[step(invoices)]} />);
    expect(screen.getByText(/2 invoices/)).toBeInTheDocument();
    expect(screen.getByText(/USD 63,382\.54/)).toBeInTheDocument(); // grouped digits, exact decimals
    await userEvent.click(screen.getByText(/^Evidence/));
    const table = screen.getByRole("table", {
      name: /invoices behind this answer/i,
    });
    expect(within(table).getByText("A-1")).toBeInTheDocument();
    expect(within(table).getByText("30,000.10")).toBeInTheDocument();
    expect(
      within(table).getByText(/invoice_A-2\.pdf · p\. 1/),
    ).toBeInTheDocument();
    expect(
      within(table).getByRole("row", { name: /^Total \(USD\)/ }),
    ).toHaveTextContent("63,382.54");
  });

  it("says when only some rows are shown and that the totals cover all of them", () => {
    const cut: Evidence = {
      ...invoices,
      count: 240,
      truncated: true,
    } as Evidence;
    render(<EvidencePanel steps={[step(cut)]} />);
    expect(screen.getByText(/showing the first 2 of 240/i)).toBeInTheDocument();
  });

  it("keeps currencies apart", async () => {
    const mixed: Evidence = {
      ...invoices,
      totals: { EUR: "70.00", USD: "350.30" },
      count: 3,
    } as Evidence;
    render(<EvidencePanel steps={[step(mixed)]} />);
    expect(screen.getByText(/EUR 70\.00/)).toBeInTheDocument();
    expect(screen.getByText(/USD 350\.30/)).toBeInTheDocument();
  });

  it("shows contract lists as a facts table", async () => {
    const contracts: Evidence = {
      kind: "contracts",
      rows: [
        {
          vendor: "Acme Labs",
          filename: "contract_acme.pdf",
          payment_terms_days: 30,
          termination_notice_days: 60,
          auto_renewal: true,
          governing_law: "State of Delaware",
        },
      ],
      count: 1,
      truncated: false,
    };
    render(
      <EvidencePanel steps={[step(contracts, { tool: "query_contracts" })]} />,
    );
    await userEvent.click(screen.getByText(/^Evidence/));
    const table = screen.getByRole("table", {
      name: /contracts behind this answer/i,
    });
    expect(within(table).getByText("Acme Labs")).toBeInTheDocument();
    expect(within(table).getByText("State of Delaware")).toBeInTheDocument();
    expect(within(table).getByText("contract_acme.pdf")).toBeInTheDocument();
  });

  it("renders nothing without evidence or without rows", () => {
    const { container, rerender } = render(
      <EvidencePanel steps={[step(undefined)]} />,
    );
    expect(container).toBeEmptyDOMElement();
    rerender(
      <EvidencePanel
        steps={[
          step({ ...invoices, rows: [], count: 0, totals: {} } as Evidence),
        ]}
      />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  it("shows only plain text, never markup from a document", async () => {
    const hostile: Evidence = {
      ...invoices,
      rows: [
        {
          ...(invoices as Extract<Evidence, { kind: "invoices" }>).rows[0],
          vendor: "<img src=x onerror=alert(1)>",
        },
      ],
      count: 1,
    } as Evidence;
    render(<EvidencePanel steps={[step(hostile)]} />);
    await userEvent.click(screen.getByText(/^Evidence/));
    expect(
      screen.getByText("<img src=x onerror=alert(1)>"),
    ).toBeInTheDocument();
    expect(document.querySelector("img")).toBeNull();
  });
});
