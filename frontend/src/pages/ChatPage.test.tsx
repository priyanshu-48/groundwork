import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { ChatMessage } from "../api/types";
import { ChatPage } from "./ChatPage";

const api = vi.hoisted(() => ({
  listConversations: vi.fn(),
  createConversation: vi.fn(),
  getMessages: vi.fn(),
  sendMessage: vi.fn(),
}));
vi.mock("../api/client", () => api);

const enc = new TextEncoder();
const sse = (events: [string, unknown][]) =>
  new Response(
    new ReadableStream({
      start(c) {
        for (const [name, data] of events) c.enqueue(enc.encode(`event: ${name}\ndata: ${JSON.stringify(data)}\n\n`));
        c.close();
      },
    }),
    { headers: { "Content-Type": "text/event-stream" } },
  );

const cite = { ref: "C1", chunk_id: "c", document_id: "d", filename: "acme.pdf", page: 3, snippet: "Net 45 applies to Acme." };
const stored: ChatMessage[] = [
  { id: "m1", role: "user", content: "What are the terms?", citations: null, created_at: "t" },
  {
    id: "m2",
    role: "assistant",
    content: "Net 45 [C1]",
    citations: [cite],
    created_at: "t",
    steps: [{ step_no: 1, tool: "search_documents", args: { query: "terms" }, status: "ok", latency_ms: 12, preview: "1 results" }],
  },
];

function renderChat(path = "/chat") {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/chat/:conversationId" element={<ChatPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  api.listConversations.mockResolvedValue([]);
  api.createConversation.mockResolvedValue({ id: "c1", title: null, created_at: "t" });
  api.getMessages.mockResolvedValue([]);
});

describe("ChatPage", () => {
  it("asks a question, shows the streamed answer with a citation chip, and opens the source", async () => {
    api.sendMessage.mockResolvedValue(
      sse([
        ["step", { step_no: 1, tool: "search_documents", args: { query: "terms" }, status: "running" }],
        ["step", { step_no: 1, tool: "search_documents", args: { query: "terms" }, status: "ok", latency_ms: 12, preview: "1 results" }],
        ["token", { text: "Net 45 [C1]" }],
        ["answer", { text: "Net 45 [C1]" }],
        ["citations", { items: [cite] }],
        ["done", { status: "ok", model: "m" }],
      ]),
    );
    api.getMessages.mockResolvedValue(stored); // what the server has stored once the run is over

    renderChat();
    await userEvent.type(screen.getByLabelText("Your question"), "What are the terms?");
    await userEvent.click(screen.getByRole("button", { name: "Ask" }));

    const chip = await screen.findByRole("button", { name: "Source C1: acme.pdf, page 3" });
    expect(api.createConversation).toHaveBeenCalledOnce();
    expect(api.sendMessage).toHaveBeenCalledWith("c1", "What are the terms?", expect.any(AbortSignal));

    await userEvent.click(chip);
    const source = screen.getByRole("complementary", { name: "Source C1" });
    expect(source).toHaveTextContent("acme.pdf");
    expect(source).toHaveTextContent("page 3");
    expect(source).toHaveTextContent("Net 45 applies to Acme.");

    // the stored message carries the steps the agent took
    await userEvent.click(await screen.findByText("Steps (1)"));
    expect(screen.getByText("search_documents")).toBeInTheDocument();
  });

  it("shows an error banner when the server reports a failed run", async () => {
    api.sendMessage.mockResolvedValue(
      sse([
        ["answer", { text: "I couldn't get an answer from the language model right now." }],
        ["citations", { items: [] }],
        ["done", { status: "error", error: "LLMUnavailable" }],
      ]),
    );
    renderChat();
    await userEvent.type(screen.getByLabelText("Your question"), "hello");
    await userEvent.click(screen.getByRole("button", { name: "Ask" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("couldn't get an answer");
  });

  it("shows a network failure instead of hanging", async () => {
    api.sendMessage.mockRejectedValue(new Error("Failed to fetch"));
    renderChat("/chat/c1");
    await userEvent.type(screen.getByLabelText("Your question"), "hello");
    await userEvent.click(screen.getByRole("button", { name: "Ask" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Failed to fetch");
  });

  it("does not send an empty question and keeps Ask disabled", async () => {
    renderChat();
    expect(screen.getByRole("button", { name: "Ask" })).toBeDisabled();
    await userEvent.type(screen.getByLabelText("Your question"), "   ");
    expect(screen.getByRole("button", { name: "Ask" })).toBeDisabled();
    expect(api.sendMessage).not.toHaveBeenCalled();
  });

  it("renders an existing conversation's history with its citations", async () => {
    api.getMessages.mockResolvedValue(stored);
    renderChat("/chat/c1");
    expect(await screen.findByText("What are the terms?")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole("button", { name: /Source C1/ })).toBeInTheDocument());
  });
});

describe("ChatPage effects", () => {
  it("never returns a value from the scroll effect (React expects a cleanup function or nothing)", async () => {
    const original = Element.prototype.scrollIntoView;
    // real browsers differ from jsdom; make the call return something to catch an accidental `return`
    Element.prototype.scrollIntoView = vi.fn(() => ({ not: "a function" })) as unknown as typeof original;
    const error = vi.spyOn(console, "error").mockImplementation(() => undefined);
    try {
      api.getMessages.mockResolvedValue(stored);
      renderChat("/chat/c1");
      await screen.findByText("What are the terms?");
      const complaints = error.mock.calls.filter((c) => String(c[0]).includes("must not return anything"));
      expect(complaints).toHaveLength(0);
    } finally {
      error.mockRestore();
      Element.prototype.scrollIntoView = original;
    }
  });
});
