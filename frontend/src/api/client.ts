import type { ChatMode, Conversation, ChatMessage, DocKind, DocumentOut } from "./types";

const TOKEN_KEY = "groundwork.token";

/**
 * The JWT lives in sessionStorage: gone when the tab closes, unlike localStorage. Either is readable
 * by any script on the page, which is why answers are rendered as plain text, never as HTML.
 */
export const tokenStore = {
  get(): string | null {
    try {
      return sessionStorage.getItem(TOKEN_KEY);
    } catch {
      return null;
    }
  },
  set(token: string): void {
    try {
      sessionStorage.setItem(TOKEN_KEY, token);
    } catch {
      /* storage blocked: the session just will not survive a reload */
    }
  },
  clear(): void {
    try {
      sessionStorage.removeItem(TOKEN_KEY);
    } catch {
      /* nothing to clear */
    }
  },
};

export class ApiError extends Error {
  readonly status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

let onUnauthorized: (() => void) | null = null;
export function setUnauthorizedHandler(fn: (() => void) | null): void {
  onUnauthorized = fn;
}

async function errorMessage(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: unknown };
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail.map((d: { msg?: string }) => d.msg ?? "invalid value").join("; ");
    }
  } catch {
    /* not JSON */
  }
  return res.statusText || `Request failed (${res.status})`;
}

async function request(path: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  const token = tokenStore.get();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(`/api${path}`, { ...init, headers });
  if (res.status === 401 && token) {
    tokenStore.clear(); // expired or invalid session: back to the login page
    onUnauthorized?.();
  }
  if (!res.ok) throw new ApiError(res.status, await errorMessage(res));
  return res;
}

const json = (body: unknown): RequestInit => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export async function login(email: string, password: string): Promise<string> {
  const res = await request("/auth/login", json({ email, password }));
  return ((await res.json()) as { access_token: string }).access_token;
}

export async function signup(
  orgName: string,
  email: string,
  password: string,
  inviteCode?: string,
): Promise<string> {
  const res = await request(
    "/auth/signup",
    json({ org_name: orgName, email, password, invite_code: inviteCode || undefined }),
  );
  return ((await res.json()) as { access_token: string }).access_token;
}

export async function listDocuments(): Promise<DocumentOut[]> {
  return (await (await request("/documents?limit=100")).json()) as DocumentOut[];
}

export async function uploadDocument(
  file: File,
  kind: DocKind,
): Promise<{ doc: DocumentOut; existing: boolean }> {
  const form = new FormData();
  form.append("file", file);
  form.append("kind", kind);
  const res = await request("/documents", { method: "POST", body: form });
  return { doc: (await res.json()) as DocumentOut, existing: res.status === 200 };
}

export async function listConversations(): Promise<Conversation[]> {
  return (await (await request("/conversations")).json()) as Conversation[];
}

export async function createConversation(): Promise<Conversation> {
  return (await (await request("/conversations", json({}))).json()) as Conversation;
}

export async function getMessages(conversationId: string): Promise<ChatMessage[]> {
  return (await (await request(`/conversations/${conversationId}/messages`)).json()) as ChatMessage[];
}

export interface Meta {
  chat: ChatMode;
  signup_code_required?: boolean;
  demo_available?: boolean;
}

export async function getMeta(): Promise<Meta> {
  return (await (await request("/meta")).json()) as Meta;
}

export async function getMe(): Promise<{ user_id: string; org_id: string; demo: boolean }> {
  return (await (await request("/auth/me")).json()) as { user_id: string; org_id: string; demo: boolean };
}

/** One click into the shared, read-only demo workspace (no credentials). */
export async function demoLogin(): Promise<string> {
  const res = await request("/auth/demo", { method: "POST" });
  return ((await res.json()) as { access_token: string }).access_token;
}

/** Starts a chat turn; the caller reads the SSE body (see api/sse.ts). */
export function sendMessage(conversationId: string, content: string, signal: AbortSignal): Promise<Response> {
  return request(`/chat/${conversationId}/messages`, { ...json({ content }), signal });
}
