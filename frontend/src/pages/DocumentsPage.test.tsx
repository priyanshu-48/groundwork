import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { DocumentOut } from "../api/types";
import { StatusBadge } from "../components/StatusBadge";
import { DocumentsPage } from "./DocumentsPage";

const api = vi.hoisted(() => ({ listDocuments: vi.fn(), uploadDocument: vi.fn() }));
vi.mock("../api/client", () => api);

const doc = (over: Partial<DocumentOut>): DocumentOut => ({
  id: "1",
  filename: "a.pdf",
  sha256: "x",
  kind: "contract",
  status: "ready",
  error: null,
  page_count: 3,
  created_at: "2026-01-01T00:00:00Z",
  ...over,
});

function renderPage() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <DocumentsPage />
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  api.listDocuments.mockResolvedValue([]);
});

describe("StatusBadge", () => {
  it.each(["pending", "processing", "ready", "failed"] as const)("shows %s as text", (s) => {
    render(<StatusBadge status={s} />);
    expect(screen.getByText(s)).toBeInTheDocument();
  });
});

describe("DocumentsPage", () => {
  it("lists documents with status, page count and the error of a failed one", async () => {
    api.listDocuments.mockResolvedValue([
      doc({ id: "1", filename: "contract.pdf", status: "ready", page_count: 4 }),
      doc({ id: "2", filename: "scan.pdf", status: "failed", error: "PDF has no extractable text", page_count: null }),
    ]);
    renderPage();
    expect(await screen.findByText("contract.pdf")).toBeInTheDocument();
    expect(screen.getByText("ready")).toBeInTheDocument();
    expect(screen.getByText("PDF has no extractable text")).toBeInTheDocument();
  });

  it("says so when there are no documents yet", async () => {
    renderPage();
    expect(await screen.findByText(/No documents yet/)).toBeInTheDocument();
  });

  it("uploads a valid PDF with the chosen type", async () => {
    api.uploadDocument.mockResolvedValue({ doc: doc({ filename: "new.pdf" }), existing: false });
    renderPage();
    await userEvent.selectOptions(screen.getByLabelText("Document type"), "invoice");
    const file = new File(["%PDF-1.4 hi"], "new.pdf", { type: "application/pdf" });
    await userEvent.upload(screen.getByLabelText("Upload PDF files"), file);
    await waitFor(() => expect(api.uploadDocument).toHaveBeenCalledWith(file, "invoice"));
  });

  it("rejects a non-PDF in the browser without calling the server", async () => {
    renderPage();
    const file = new File(["hello"], "notes.txt", { type: "text/plain" });
    await userEvent.upload(screen.getByLabelText("Upload PDF files"), file, { applyAccept: false });
    expect(await screen.findByRole("alert")).toHaveTextContent("notes.txt: only PDF files are accepted");
    expect(api.uploadDocument).not.toHaveBeenCalled();
  });

  it("mentions when a file was already uploaded", async () => {
    api.uploadDocument.mockResolvedValue({ doc: doc({ filename: "dup.pdf" }), existing: true });
    renderPage();
    await userEvent.upload(screen.getByLabelText("Upload PDF files"), new File(["%PDF-1.4"], "dup.pdf", { type: "application/pdf" }));
    expect(await screen.findByText("dup.pdf: already uploaded")).toBeInTheDocument();
  });

  it("shows the server's message when an upload fails", async () => {
    api.uploadDocument.mockRejectedValue(new Error("File exceeds 20 MB limit"));
    renderPage();
    await userEvent.upload(screen.getByLabelText("Upload PDF files"), new File(["%PDF-1.4"], "big.pdf", { type: "application/pdf" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("big.pdf: File exceeds 20 MB limit");
  });
});
