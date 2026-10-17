import { describe, expect, it } from "vitest";
import type { DocumentOut } from "../api/types";
import { documentsRefetchInterval, MAX_UPLOAD_BYTES, validateUpload } from "./upload";

const doc = (status: DocumentOut["status"]): DocumentOut => ({
  id: status,
  filename: `${status}.pdf`,
  sha256: "x",
  kind: "contract",
  status,
  error: null,
  page_count: null,
  created_at: "2026-01-01T00:00:00Z",
});

describe("validateUpload", () => {
  it("accepts a normal PDF by MIME type or by extension", () => {
    expect(validateUpload({ name: "a.pdf", size: 10, type: "application/pdf" })).toBeNull();
    expect(validateUpload({ name: "SCAN.PDF", size: 10, type: "" })).toBeNull();
  });

  it("rejects non-PDFs, empty files and files over 20 MB, naming the file", () => {
    expect(validateUpload({ name: "a.docx", size: 10, type: "application/msword" })).toMatch(/a\.docx.*only PDF/);
    expect(validateUpload({ name: "a.pdf", size: 0, type: "application/pdf" })).toMatch(/empty/);
    expect(validateUpload({ name: "big.pdf", size: MAX_UPLOAD_BYTES + 1, type: "application/pdf" })).toMatch(/20 MB/);
    expect(validateUpload({ name: "edge.pdf", size: MAX_UPLOAD_BYTES, type: "application/pdf" })).toBeNull();
  });
});

describe("documentsRefetchInterval", () => {
  it("polls while something is pending or processing", () => {
    expect(documentsRefetchInterval([doc("ready"), doc("pending")])).toBe(2000);
    expect(documentsRefetchInterval([doc("processing")])).toBe(2000);
  });

  it("stops once every document is ready or failed, and before data arrives", () => {
    expect(documentsRefetchInterval([doc("ready"), doc("failed")])).toBe(false);
    expect(documentsRefetchInterval([])).toBe(false);
    expect(documentsRefetchInterval(undefined)).toBe(false);
  });
});
