import type { DocumentOut } from "../api/types";

export const MAX_UPLOAD_BYTES = 20 * 1024 * 1024; // mirrors the server's limit

/** Client-side check so obvious mistakes fail fast; the server still enforces everything. */
export function validateUpload(file: Pick<File, "name" | "size" | "type">): string | null {
  const looksLikePdf = file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
  if (!looksLikePdf) return `${file.name}: only PDF files are accepted`;
  if (file.size === 0) return `${file.name}: the file is empty`;
  if (file.size > MAX_UPLOAD_BYTES) return `${file.name}: larger than 20 MB`;
  return null;
}

/** Poll while anything is still being processed, then stop. */
export function documentsRefetchInterval(docs: DocumentOut[] | undefined): number | false {
  return docs?.some((d) => d.status === "pending" || d.status === "processing") ? 2000 : false;
}
