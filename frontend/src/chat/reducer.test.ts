import { describe, expect, it } from "vitest";
import type { StreamEvent } from "../api/types";
import { idle, reducer, type RunState } from "./reducer";

function run(events: StreamEvent[], start: RunState = reducer(idle, { type: "start" })): RunState {
  return events.reduce((s, event) => reducer(s, { type: "event", event }), start);
}

const step = (n: number, status: "running" | "ok" | "error", extra = {}): StreamEvent => ({
  type: "step",
  data: { step_no: n, tool: "search_documents", args: { query: "x" }, status, ...extra },
});

describe("chat run reducer", () => {
  it("accumulates streamed tokens", () => {
    const s = run([
      { type: "token", data: { text: "Hel" } },
      { type: "token", data: { text: "lo" } },
    ]);
    expect(s.text).toBe("Hello");
    expect(s.status).toBe("streaming");
  });

  it("the final answer replaces the streamed text (a streamed [C99] never survives)", () => {
    const s = run([
      { type: "token", data: { text: "Hello [C99]" } },
      { type: "answer", data: { text: "Hello" } },
    ]);
    expect(s.answer).toBe("Hello");
    expect(s.text).toBe("");
  });

  it("updates a step in place and keeps latency and preview", () => {
    const s = run([step(1, "running"), step(1, "ok", { latency_ms: 42, preview: "3 results" })]);
    expect(s.steps).toHaveLength(1);
    expect(s.steps[0]).toMatchObject({ status: "ok", latency_ms: 42, preview: "3 results", tool: "search_documents" });
  });

  it("drops a streamed preface when the model goes on to call a tool", () => {
    const s = run([{ type: "token", data: { text: "Let me check. " } }, step(1, "running")]);
    expect(s.text).toBe("");
  });

  it("keeps the streamed answer text when a step finishes after it", () => {
    const s = run([step(1, "running"), { type: "token", data: { text: "Answer" } }, step(1, "ok")]);
    expect(s.text).toBe("Answer");
  });

  it("stores citations and finishes with done", () => {
    const cite = { ref: "C1", chunk_id: "c", document_id: "d", filename: "a.pdf", page: 2, snippet: "s" };
    const s = run([
      { type: "citations", data: { items: [cite] } },
      { type: "done", data: { status: "ok", model: "m", latency_ms: 10 } },
    ]);
    expect(s.citations).toEqual([cite]);
    expect(s.status).toBe("done");
    expect(s.done?.model).toBe("m");
  });

  it("a done event with status error is an error state that keeps the server's message", () => {
    const s = run([
      { type: "answer", data: { text: "I couldn't get an answer right now." } },
      { type: "done", data: { status: "error" } },
    ]);
    expect(s.status).toBe("error");
    expect(s.error).toBe("I couldn't get an answer right now.");
  });

  it("an error event and a network failure both end in an error state", () => {
    expect(run([{ type: "error", data: { message: "boom" } }]).error).toBe("boom");
    expect(reducer(reducer(idle, { type: "start" }), { type: "fail", message: "offline" }).error).toBe("offline");
  });

  it("start clears the previous run; reset returns to idle", () => {
    const dirty = run([{ type: "token", data: { text: "old" } }]);
    expect(reducer(dirty, { type: "start" }).text).toBe("");
    expect(reducer(dirty, { type: "reset" })).toEqual(idle);
  });
});
