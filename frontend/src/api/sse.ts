import type { StreamEvent } from "./types";

export interface RawSSE {
  event: string;
  data: string;
}

/**
 * Parse a Server-Sent Events byte stream. We cannot use EventSource: it only does GET and cannot
 * send an Authorization header. Handles events split across chunks (even inside a multi-byte
 * character), LF / CRLF / CR line endings, multi-line data, comments and keep-alives.
 */
export async function* parseSSE(stream: ReadableStream<Uint8Array>): AsyncGenerator<RawSSE> {
  const reader = stream.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";
  try {
    for (;;) {
      const { value, done } = await reader.read();
      if (value) buffer += decoder.decode(value, { stream: true });
      if (done) buffer += decoder.decode();
      // normalise line endings so "\r\n\r\n" and "\r\r" end an event like "\n\n"
      // (a lone trailing \r may be half of \r\n, so it waits for more data unless the stream ended)
      buffer = buffer.replace(/\r\n/g, "\n").replace(done ? /\r/g : /\r(?!$)/g, "\n");
      let end: number;
      while ((end = buffer.indexOf("\n\n")) !== -1) {
        const raw = buffer.slice(0, end);
        buffer = buffer.slice(end + 2);
        const ev = toEvent(raw);
        if (ev) yield ev;
      }
      if (done) break;
    }
    // A trailing event without its closing blank line is incomplete: the connection dropped
    // mid-event, so it is discarded rather than delivered half-parsed.
  } finally {
    reader.releaseLock();
  }
}

function toEvent(block: string): RawSSE | null {
  let event = "message";
  const data: string[] = [];
  for (const line of block.split("\n")) {
    if (line === "" || line.startsWith(":")) continue; // blank or comment / keep-alive
    const colon = line.indexOf(":");
    const field = colon === -1 ? line : line.slice(0, colon);
    let value = colon === -1 ? "" : line.slice(colon + 1);
    if (value.startsWith(" ")) value = value.slice(1);
    if (field === "event") event = value;
    else if (field === "data") data.push(value);
  }
  return data.length ? { event, data: data.join("\n") } : null;
}

const KNOWN = new Set(["step", "token", "answer", "citations", "done", "error"]);

/** Turn a raw event into a typed one; unknown event names and bad JSON are ignored. */
export function toStreamEvent(raw: RawSSE): StreamEvent | null {
  if (!KNOWN.has(raw.event)) return null;
  try {
    return { type: raw.event, data: JSON.parse(raw.data) } as StreamEvent;
  } catch {
    return null;
  }
}

export async function* chatEvents(stream: ReadableStream<Uint8Array>): AsyncGenerator<StreamEvent> {
  for await (const raw of parseSSE(stream)) {
    const ev = toStreamEvent(raw);
    if (ev) yield ev;
  }
}
