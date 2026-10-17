import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthProvider } from "../auth";
import { Layout } from "../components/Layout";
import { ChatPage } from "./ChatPage";
import { DocumentsPage } from "./DocumentsPage";
import { LoginPage } from "./LoginPage";

const api = vi.hoisted(() => ({
  login: vi.fn(),
  signup: vi.fn(),
  demoLogin: vi.fn(),
  getMeta: vi.fn(),
  getMe: vi.fn(),
  listDocuments: vi.fn(),
  uploadDocument: vi.fn(),
  listConversations: vi.fn(),
  createConversation: vi.fn(),
  getMessages: vi.fn(),
  sendMessage: vi.fn(),
  tokenStore: { get: (): string | null => "t", set: vi.fn(), clear: vi.fn() },
  setUnauthorizedHandler: vi.fn(),
}));
vi.mock("../api/client", () => api);

function wrap(ui: React.ReactNode, path = "/") {
  return render(
    <QueryClientProvider
      client={
        new QueryClient({ defaultOptions: { queries: { retry: false } } })
      }
    >
      <MemoryRouter initialEntries={[path]}>
        <AuthProvider>{ui}</AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  api.getMeta.mockResolvedValue({
    chat: "model",
    signup_code_required: false,
    demo_available: true,
  });
  api.getMe.mockResolvedValue({ user_id: "u", org_id: "o", demo: true });
  api.listDocuments.mockResolvedValue([]);
  api.listConversations.mockResolvedValue([]);
  api.getMessages.mockResolvedValue([]);
  api.createConversation.mockResolvedValue({
    id: "c1",
    title: null,
    created_at: "t",
  });
});

describe("demo login", () => {
  it("offers the demo and signs in with its token", async () => {
    api.tokenStore.get = () => null;
    api.demoLogin.mockResolvedValue("demo-token");
    wrap(<LoginPage />);
    await userEvent.click(
      await screen.findByRole("button", { name: /try the demo/i }),
    );
    await waitFor(() =>
      expect(api.tokenStore.set).toHaveBeenCalledWith("demo-token"),
    );
    api.tokenStore.get = () => "t";
  });

  it("hides the button when the server has no demo", async () => {
    api.tokenStore.get = () => null;
    api.getMeta.mockResolvedValue({
      chat: "model",
      signup_code_required: false,
      demo_available: false,
    });
    wrap(<LoginPage />);
    await screen.findByRole("button", { name: "Sign in" });
    expect(
      screen.queryByRole("button", { name: /try the demo/i }),
    ).not.toBeInTheDocument();
    api.tokenStore.get = () => "t";
  });
});

describe("demo workspace", () => {
  it("shows a read-only banner for demo users and not for others", async () => {
    const { unmount } = wrap(
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<p>home</p>} />
        </Route>
      </Routes>,
    );
    expect(
      await screen.findByText(/shared demo workspace/i),
    ).toBeInTheDocument();
    unmount();
    api.getMe.mockResolvedValue({ user_id: "u", org_id: "o", demo: false });
    wrap(
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<p>home</p>} />
        </Route>
      </Routes>,
    );
    await screen.findByText("home");
    expect(
      screen.queryByText(/shared demo workspace/i),
    ).not.toBeInTheDocument();
  });

  it("hides uploading for demo users", async () => {
    wrap(<DocumentsPage />);
    expect(await screen.findByText(/read-only/i)).toBeInTheDocument();
    expect(screen.queryByLabelText("Upload PDF files")).not.toBeInTheDocument();
  });

  it("keeps uploading for ordinary users", async () => {
    api.getMe.mockResolvedValue({ user_id: "u", org_id: "o", demo: false });
    wrap(<DocumentsPage />);
    expect(
      await screen.findByLabelText("Upload PDF files"),
    ).toBeInTheDocument();
  });

  it("offers suggested questions that send themselves", async () => {
    const enc = new TextEncoder();
    api.sendMessage.mockResolvedValue(
      new Response(
        new ReadableStream({
          start(c) {
            c.enqueue(enc.encode('event: done\ndata: {"status":"ok"}\n\n'));
            c.close();
          },
        }),
      ),
    );
    wrap(
      <Routes>
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/chat/:conversationId" element={<ChatPage />} />
      </Routes>,
      "/chat",
    );
    const chip = await screen.findByRole("button", {
      name: /termination notice period in the Kestrel/i,
    });
    await userEvent.click(chip);
    await waitFor(() =>
      expect(api.sendMessage).toHaveBeenCalledWith(
        "c1",
        expect.stringContaining("Kestrel Security"),
        expect.anything(),
      ),
    );
  });

  it("shows no suggestions to ordinary users", async () => {
    api.getMe.mockResolvedValue({ user_id: "u", org_id: "o", demo: false });
    wrap(
      <Routes>
        <Route path="/chat" element={<ChatPage />} />
      </Routes>,
      "/chat",
    );
    await screen.findByText(/ask a question/i);
    expect(
      screen.queryByRole("button", { name: /Kestrel/i }),
    ).not.toBeInTheDocument();
  });
});
