import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useReducer, useRef, useState, type FormEvent, type KeyboardEvent, type ReactNode } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { createConversation, getMessages, listConversations, sendMessage } from "../api/client";
import { chatEvents } from "../api/sse";
import type { Citation } from "../api/types";
import { idle, reducer } from "../chat/reducer";
import { CitationDetail } from "../components/CitationDetail";
import { CitedText } from "../components/CitedText";
import { StepsPanel } from "../components/StepsPanel";

function Bubble({ role, children }: { role: "user" | "assistant"; children: ReactNode }) {
  const mine = role === "user";
  return (
    <div className={`flex ${mine ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[85%] rounded-lg px-4 py-2 ${mine ? "bg-slate-900 text-white" : "bg-white shadow"}`}>
        {children}
      </div>
    </div>
  );
}

function AnswerWithSources({ text, citations }: { text: string; citations: Citation[] }) {
  const [selected, setSelected] = useState<string | null>(null);
  const chosen = citations.find((c) => c.ref === selected) ?? null;
  return (
    <>
      <CitedText text={text} citations={citations} selected={selected} onSelect={setSelected} />
      {chosen && <CitationDetail citation={chosen} onClose={() => setSelected(null)} />}
    </>
  );
}

export function ChatPage() {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [run, dispatch] = useReducer(reducer, idle);
  const [pending, setPending] = useState<string | null>(null); // the question being answered
  const [draft, setDraft] = useState("");
  const abort = useRef<AbortController | null>(null);
  const bottom = useRef<HTMLDivElement>(null);

  const conversations = useQuery({ queryKey: ["conversations"], queryFn: listConversations });
  const history = useQuery({
    queryKey: ["messages", conversationId],
    queryFn: () => getMessages(conversationId!),
    enabled: !!conversationId,
  });

  useEffect(() => () => abort.current?.abort(), []);
  useEffect(() => {
    // braces on purpose: an effect must not return scrollIntoView's result (React expects cleanup)
    bottom.current?.scrollIntoView?.({ block: "end" });
  }, [history.data, run.text, run.answer]);

  const busy = pending !== null;

  // Switching conversation from the sidebar drops the previous run's live state. (Not done in an
  // effect or with a key: creating a conversation also changes the URL, and that must keep the
  // run that is in progress, including its error message.)
  const switchTo = (go: () => void) => (e?: { preventDefault: () => void }) => {
    if (busy) return e?.preventDefault(); // never switch while an answer is streaming
    dispatch({ type: "reset" });
    go();
  };

  async function send(text: string) {
    let id = conversationId;
    try {
      id ??= (await createConversation()).id;
    } catch (e) {
      dispatch({ type: "fail", message: (e as Error).message });
      return;
    }
    setPending(text);
    dispatch({ type: "start" }); // also clears any previous error
    abort.current = new AbortController();
    try {
      const res = await sendMessage(id, text, abort.current.signal);
      if (!res.body) throw new Error("The server sent no response body");
      for await (const event of chatEvents(res.body)) dispatch({ type: "event", event });
    } catch (e) {
      if ((e as Error).name !== "AbortError") dispatch({ type: "fail", message: (e as Error).message });
    } finally {
      // Load the stored conversation before dropping the live view, so nothing flashes empty.
      // (fetchQuery, not invalidate: for a brand-new conversation nothing observes the query yet.)
      try {
        await queryClient.fetchQuery({ queryKey: ["messages", id], queryFn: () => getMessages(id), staleTime: 0 });
      } catch {
        /* the live view is dropped anyway; the error banner already says what went wrong */
      }
      void queryClient.invalidateQueries({ queryKey: ["conversations"] });
      setPending(null);
      if (!conversationId) navigate(`/chat/${id}`, { replace: true }); // first message of a new chat
    }
  }

  const submit = (e: FormEvent) => {
    e.preventDefault();
    const text = draft.trim();
    if (!text || busy) return;
    setDraft("");
    void send(text);
  };

  const onKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) submit(e);
  };

  const messages = history.data ?? [];
  return (
    <div className="flex h-full">
      <aside className="hidden w-64 shrink-0 flex-col border-r border-slate-200 bg-white md:flex" aria-label="Conversations">
        <div className="p-3">
          <button
            type="button"
            onClick={switchTo(() => navigate("/chat"))}
            className="w-full rounded bg-slate-900 px-3 py-2 text-sm font-medium text-white"
          >
            New chat
          </button>
        </div>
        <ul className="flex-1 overflow-auto px-2 pb-2">
          {conversations.data?.map((c) => (
            <li key={c.id}>
              <Link
                to={`/chat/${c.id}`}
                onClick={switchTo(() => undefined)}
                className={`block truncate rounded px-3 py-2 text-sm ${c.id === conversationId ? "bg-slate-200 font-medium" : "hover:bg-slate-100"}`}
              >
                {c.title ?? "New conversation"}
              </Link>
            </li>
          ))}
        </ul>
      </aside>

      <section className="flex min-w-0 flex-1 flex-col">
        <div className="flex-1 space-y-3 overflow-auto p-4" aria-label="Conversation">
          {messages.length === 0 && !busy && (
            <p className="mt-10 text-center text-slate-500">Ask a question about your contracts and invoices.</p>
          )}
          {messages.map((m) => (
            <div key={m.id}>
              <Bubble role={m.role}>
                {m.role === "assistant" ? (
                  <AnswerWithSources text={m.content} citations={m.citations ?? []} />
                ) : (
                  <span className="whitespace-pre-wrap">{m.content}</span>
                )}
              </Bubble>
              {m.role === "assistant" && m.steps && <StepsPanel steps={m.steps} />}
            </div>
          ))}
          {busy && (
            <div>
              <Bubble role="user">
                <span className="whitespace-pre-wrap">{pending}</span>
              </Bubble>
              <div className="mt-3" />
              <Bubble role="assistant">
                <div aria-live="polite" aria-busy={run.status === "streaming"}>
                  {run.answer !== null ? (
                    <AnswerWithSources text={run.answer} citations={run.citations} />
                  ) : run.text ? (
                    <span className="whitespace-pre-wrap">{run.text}</span>
                  ) : (
                    <span className="text-slate-500">Working on it...</span>
                  )}
                </div>
              </Bubble>
              <StepsPanel steps={run.steps} />
            </div>
          )}
          {run.status === "error" && (
            <p role="alert" className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800">
              {run.error}
            </p>
          )}
          <div ref={bottom} />
        </div>

        <form onSubmit={submit} className="border-t border-slate-200 bg-white p-3">
          <div className="flex items-end gap-2">
            <textarea
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={onKey}
              maxLength={2000}
              rows={2}
              aria-label="Your question"
              placeholder="e.g. What are the payment terms in the Acme contract?"
              className="flex-1 resize-none rounded border border-slate-300 px-3 py-2 focus:outline-2 focus:outline-indigo-500"
            />
            <button
              type="submit"
              disabled={busy || draft.trim() === ""}
              className="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {busy ? "Answering..." : "Ask"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
