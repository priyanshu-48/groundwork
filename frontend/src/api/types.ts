export type DocKind = "invoice" | "contract" | "other";
export type DocStatus = "pending" | "processing" | "ready" | "failed";

export interface DocumentOut {
  id: string;
  filename: string;
  sha256: string;
  kind: DocKind;
  status: DocStatus;
  error: string | null;
  page_count: number | null;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string | null;
  created_at: string;
}

export interface Citation {
  ref: string;
  chunk_id: string;
  document_id: string;
  filename: string;
  page: number;
  snippet: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations: Citation[] | null;
  created_at: string;
  model?: string | null;
  /** Tool calls the agent made for this answer (assistant messages only). */
  steps?: StepData[] | null;
}

export interface InvoiceEvidenceRow {
  invoice_number: string;
  vendor: string;
  issue_date: string;
  due_date?: string | null;
  currency: string | null;
  total: string; // money stays a string from the database to the screen
  filename: string | null;
  page: number | null;
}

export interface ContractEvidenceRow {
  vendor: string | null;
  filename: string | null;
  payment_terms_days?: number | null;
  late_fee_percent?: string | null;
  termination_notice_days?: number | null;
  auto_renewal?: boolean | null;
  liability_cap_amount?: string | null;
  liability_cap_currency?: string | null;
  governing_law?: string | null;
}

/** The rows behind a computed answer (invoice sums, contract lists), stored with the step. */
export type Evidence =
  | { kind: "invoices"; rows: InvoiceEvidenceRow[]; totals: Record<string, string>; count: number; truncated: boolean }
  | { kind: "contracts"; rows: ContractEvidenceRow[]; count: number; truncated: boolean };

export interface StepData {
  step_no: number;
  tool: string;
  args: Record<string, unknown>;
  status: "running" | "ok" | "error";
  latency_ms?: number;
  preview?: string;
  evidence?: Evidence;
}

export interface DoneData {
  status: "ok" | "error" | "max_steps";
  error?: string | null;
  model?: string | null;
  prompt_tokens?: number;
  completion_tokens?: number;
  latency_ms?: number;
  message_id?: string;
  run_id?: string;
  dropped_citations?: number;
}

/** What the server streams: SPEC 6.6 (step, token, citations, done, error) plus the final answer. */
export type StreamEvent =
  | { type: "step"; data: StepData }
  | { type: "token"; data: { text: string } }
  | { type: "answer"; data: { text: string } }
  | { type: "citations"; data: { items: Citation[] } }
  | { type: "done"; data: DoneData }
  | { type: "error"; data: { message: string } };

export type ChatMode = "model" | "demo" | "unavailable";
