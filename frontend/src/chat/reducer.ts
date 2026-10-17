import type { Citation, DoneData, StepData, StreamEvent } from "../api/types";

export interface RunState {
  status: "idle" | "streaming" | "done" | "error";
  /** Text streamed so far for the turn in progress (raw, not yet citation-validated). */
  text: string;
  /** The final, citation-validated answer; replaces `text` once it arrives. */
  answer: string | null;
  citations: Citation[];
  steps: StepData[];
  error: string | null;
  done: DoneData | null;
}

export const idle: RunState = {
  status: "idle",
  text: "",
  answer: null,
  citations: [],
  steps: [],
  error: null,
  done: null,
};

export type Action =
  | { type: "start" }
  | { type: "event"; event: StreamEvent }
  | { type: "fail"; message: string }
  | { type: "reset" };

export function reducer(state: RunState, action: Action): RunState {
  switch (action.type) {
    case "start":
      return { ...idle, status: "streaming" };
    case "reset":
      return idle;
    case "fail":
      return { ...state, status: "error", error: action.message };
    case "event":
      return applyEvent(state, action.event);
  }
}

function applyEvent(s: RunState, ev: StreamEvent): RunState {
  switch (ev.type) {
    case "token":
      return { ...s, text: s.text + ev.data.text };
    case "step": {
      const i = s.steps.findIndex((x) => x.step_no === ev.data.step_no);
      const steps = i === -1 ? [...s.steps, ev.data] : s.steps.map((x, j) => (j === i ? { ...x, ...ev.data } : x));
      // A turn that goes on to call a tool may have streamed a preface; drop it, the real
      // answer comes after the tools finish.
      return { ...s, steps, text: ev.data.status === "running" ? "" : s.text };
    }
    case "answer":
      return { ...s, answer: ev.data.text, text: "" };
    case "citations":
      return { ...s, citations: ev.data.items };
    case "done":
      return {
        ...s,
        done: ev.data,
        status: ev.data.status === "error" ? "error" : "done",
        error: ev.data.status === "error" ? (s.answer ?? "The answer could not be completed.") : null,
      };
    case "error":
      return { ...s, status: "error", error: ev.data.message };
  }
}
