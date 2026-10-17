import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthProvider } from "../auth";
import { LoginPage } from "./LoginPage";

const api = vi.hoisted(() => ({
  login: vi.fn(),
  signup: vi.fn(),
  getMeta: vi.fn(),
  tokenStore: { get: () => null, set: vi.fn(), clear: vi.fn() },
  setUnauthorizedHandler: vi.fn(),
}));
vi.mock("../api/client", () => api);

function renderPage() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  api.signup.mockResolvedValue("token");
});

async function openSignup() {
  await userEvent.click(screen.getByRole("button", { name: /create a workspace/i }));
}

describe("LoginPage invite code", () => {
  it("shows no invite field when the server does not require one", async () => {
    api.getMeta.mockResolvedValue({ chat: "model", signup_code_required: false });
    renderPage();
    await openSignup();
    expect(screen.queryByLabelText("Invite code")).not.toBeInTheDocument();
  });

  it("asks for the code and sends it with the signup when required", async () => {
    api.getMeta.mockResolvedValue({ chat: "model", signup_code_required: true });
    renderPage();
    await openSignup();
    await userEvent.type(await screen.findByLabelText("Invite code"), "open-sesame");
    await userEvent.type(screen.getByLabelText("Company name"), "Acme");
    await userEvent.type(screen.getByLabelText("Email"), "a@example.com");
    await userEvent.type(screen.getByLabelText(/^Password/), "a-long-password");
    await userEvent.click(screen.getByRole("button", { name: "Create account" }));
    expect(api.signup).toHaveBeenCalledWith("Acme", "a@example.com", "a-long-password", "open-sesame");
  });
});
