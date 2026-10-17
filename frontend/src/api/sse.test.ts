import { describe, expect, it } from "vitest";
import { chatEvents, parseSSE, toStreamEvent } from "./sse";

const enc = new TextEncoder();

/** A ReadableStream that delivers the given byte chunks one by one. */
function streamOf(...chunks: (string | Uint8Array)[]): ReadableStream<Uint8Array> {
  return new ReadableStream({
    start(controller) {
      for (const c of chunks) controller.enqueue(typeof c === "string" ? enc.encode(c) : c);
      controller.close();
    },
  });
}

async function collect<T>(gen: AsyncGenerator<T>): Promise<T[]> {
  const out: T[] = [];
  for await (const x of gen) out.push(x);
  return out;
}

describe("parseSSE", () => {
  it("parses a simple event", async () => {
    const out = await collect(parseSSE(streamOf('event: token\ndata: {"text":"hi"}\n\n')));
    expect(out).toEqual([{ event: "token", data: '{"text":"hi"}' }]);
  });

  it("reassembles an event split across chunks, even mid-line", async () => {
    const out = await collect(parseSSE(streamOf("event: tok", 'en\ndata: {"te', 'xt":"a"}\n', "\n")));
    expect(out).toEqual([{ event: "token", data: '{"text":"a"}' }]);
  });

  it("does not corrupt a multi-byte character split between chunks", async () => {
    const bytes = enc.encode('event: token\ndata: {"text":"café €"}\n\n');
    const cut = bytes.indexOf(0xc3) + 1; // between the two bytes of "é"
    const out = await collect(parseSSE(streamOf(bytes.slice(0, cut), bytes.slice(cut))));
    expect(JSON.parse(out[0]!.data).text).toBe("café €");
  });

  it("handles CRLF and bare CR line endings", async () => {
    const out = await collect(parseSSE(streamOf("event: a\r\ndata: 1\r\n\r\nevent: b\rdata: 2\r\r")));
    expect(out).toEqual([
      { event: "a", data: "1" },
      { event: "b", data: "2" },
    ]);
  });

  it("joins multiple data lines with a newline", async () => {
    const out = await collect(parseSSE(streamOf("event: x\ndata: one\ndata: two\n\n")));
    expect(out[0]!.data).toBe("one\ntwo");
  });

  it("ignores comments and keep-alives and defaults the event name to message", async () => {
    const out = await collect(parseSSE(streamOf(": keep-alive\n\n: ping\ndata: hi\n\n")));
    expect(out).toEqual([{ event: "message", data: "hi" }]);
  });

  it("delivers several events from one chunk, in order", async () => {
    const out = await collect(parseSSE(streamOf("event: a\ndata: 1\n\nevent: b\ndata: 2\n\nevent: c\ndata: 3\n\n")));
    expect(out.map((e) => e.event)).toEqual(["a", "b", "c"]);
  });

  it("drops a trailing event that never got its closing blank line", async () => {
    const out = await collect(parseSSE(streamOf("event: a\ndata: 1\n\nevent: b\ndata: par")));
    expect(out.map((e) => e.event)).toEqual(["a"]);
  });

  it("accepts data with no space after the colon", async () => {
    const out = await collect(parseSSE(streamOf("event:x\ndata:y\n\n")));
    expect(out).toEqual([{ event: "x", data: "y" }]);
  });
});

describe("toStreamEvent / chatEvents", () => {
  it("types known events and ignores unknown names and bad JSON", async () => {
    expect(toStreamEvent({ event: "token", data: '{"text":"a"}' })).toEqual({ type: "token", data: { text: "a" } });
    expect(toStreamEvent({ event: "mystery", data: "{}" })).toBeNull();
    expect(toStreamEvent({ event: "token", data: "not json" })).toBeNull();
  });

  it("streams typed events end to end", async () => {
    const body =
      'event: step\ndata: {"step_no":1,"tool":"search_documents","args":{},"status":"running"}\n\n' +
      'event: token\ndata: {"text":"Hello"}\n\n' +
      'event: done\ndata: {"status":"ok"}\n\n';
    const events = await collect(chatEvents(streamOf(body)));
    expect(events.map((e) => e.type)).toEqual(["step", "token", "done"]);
  });
});
