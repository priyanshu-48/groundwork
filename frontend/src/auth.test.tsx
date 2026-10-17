import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { listDocuments, tokenStore } from "./api/client";
import { AuthProvider, RequireAuth } from "./auth";

function app(initial = "/secret") {
  return render(
    <QueryClientProvider client={new QueryClient()}>
      <MemoryRouter initialEntries={[initial]}>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<p>login page</p>} />
            <Route
              path="/secret"
              element={
                <RequireAuth>
                  <p>secret content</p>
                </RequireAuth>
              }
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

beforeEach(() => tokenStore.clear());
afterEach(() => vi.unstubAllGlobals());

describe("RequireAuth", () => {
  it("sends a signed-out visitor to the login page", () => {
    app();
    expect(screen.getByText("login page")).toBeInTheDocument();
    expect(screen.queryByText("secret content")).not.toBeInTheDocument();
  });

  it("lets a signed-in user through", () => {
    tokenStore.set("a-token");
    app();
    expect(screen.getByText("secret content")).toBeInTheDocument();
  });

  it("a 401 from the API ends the session and returns to login", async () => {
    tokenStore.set("expired-token");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Not authenticated" }), { status: 401 })),
    );
    app();
    expect(screen.getByText("secret content")).toBeInTheDocument();

    await expect(listDocuments()).rejects.toMatchObject({ status: 401 });

    await waitFor(() => expect(screen.getByText("login page")).toBeInTheDocument());
    expect(tokenStore.get()).toBeNull();
  });

  it("sends the token as a bearer header and prefixes calls with /api", async () => {
    tokenStore.set("abc");
    const fetchMock = vi.fn().mockResolvedValue(new Response("[]", { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    await listDocuments();
    const [url, init] = fetchMock.mock.calls[0]!;
    expect(url).toBe("/api/documents?limit=100");
    expect(new Headers((init as RequestInit).headers).get("Authorization")).toBe("Bearer abc");
  });

  it("a failed login (no token yet) is an ordinary error, not a session expiry", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Invalid credentials" }), { status: 401 })),
    );
    const { login } = await import("./api/client");
    await expect(login("a@b.c", "wrong-password")).rejects.toThrow("Invalid credentials");
  });
});
