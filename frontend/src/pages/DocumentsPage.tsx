import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRef, useState, type DragEvent } from "react";
import { listDocuments, uploadDocument } from "../api/client";
import type { DocKind } from "../api/types";
import { useIsDemo } from "../useIsDemo";
import { StatusBadge } from "../components/StatusBadge";
import { documentsRefetchInterval, validateUpload } from "../documents/upload";

export function DocumentsPage() {
  const queryClient = useQueryClient();
  const isDemo = useIsDemo();
  const input = useRef<HTMLInputElement>(null);
  const [kind, setKind] = useState<DocKind>("contract");
  const [dragging, setDragging] = useState(false);
  const [notes, setNotes] = useState<{ text: string; error: boolean }[]>([]);

  const docs = useQuery({
    queryKey: ["documents"],
    queryFn: listDocuments,
    refetchInterval: (q) => documentsRefetchInterval(q.state.data),
  });

  const upload = useMutation({
    mutationFn: (file: File) => uploadDocument(file, kind),
    onSuccess: ({ doc, existing }) => {
      if (existing)
        setNotes((n) => [
          ...n,
          { text: `${doc.filename}: already uploaded`, error: false },
        ]);
      void queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
    onError: (e: Error, file) =>
      setNotes((n) => [
        ...n,
        { text: `${file.name}: ${e.message}`, error: true },
      ]),
  });

  const addFiles = (files: FileList | File[]) => {
    setNotes([]);
    for (const file of Array.from(files)) {
      const problem = validateUpload(file);
      if (problem) setNotes((n) => [...n, { text: problem, error: true }]);
      else upload.mutate(file);
    }
  };

  const onDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragging(false);
    addFiles(e.dataTransfer.files);
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-6">
      <h1 className="text-xl font-semibold">Documents</h1>

      {isDemo && (
        <p className="rounded bg-slate-100 p-4 text-sm text-slate-700">
          This demo workspace is read-only: browse the synthetic documents
          below, then ask about them in Chat. Create your own workspace to
          upload files.
        </p>
      )}
      {!isDemo && (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          className={`rounded-lg border-2 border-dashed p-8 text-center ${dragging ? "border-indigo-500 bg-indigo-50" : "border-slate-300 bg-white"}`}
        >
          <p className="text-slate-700">Drag PDF files here, or</p>
          <button
            type="button"
            onClick={() => input.current?.click()}
            className="mt-2 rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white"
          >
            Choose files
          </button>
          <input
            ref={input}
            type="file"
            accept="application/pdf,.pdf"
            multiple
            aria-label="Upload PDF files"
            className="sr-only"
            onChange={(e) => {
              if (e.target.files) addFiles(e.target.files);
              e.target.value = ""; // allow choosing the same file again
            }}
          />
          <label className="mt-4 flex items-center justify-center gap-2 text-sm">
            Document type
            <select
              value={kind}
              onChange={(e) => setKind(e.target.value as DocKind)}
              className="rounded border border-slate-300 px-2 py-1"
            >
              <option value="contract">Contract</option>
              <option value="invoice">Invoice</option>
              <option value="other">Other</option>
            </select>
          </label>
          <p className="mt-2 text-xs text-slate-500">
            PDF only, up to 20 MB each.
          </p>
        </div>
      )}

      {upload.isPending && <p role="status">Uploading...</p>}
      {notes.length > 0 && (
        <ul className="space-y-1 text-sm">
          {notes.map((n, i) => (
            <li
              key={i}
              role={n.error ? "alert" : "status"}
              className={n.error ? "text-red-700" : "text-slate-600"}
            >
              {n.text}
            </li>
          ))}
        </ul>
      )}

      {docs.isLoading && <p>Loading documents...</p>}
      {docs.error && (
        <p role="alert" className="text-red-700">
          {docs.error.message}
        </p>
      )}
      {docs.data && docs.data.length === 0 && (
        <p className="text-slate-600">
          No documents yet. Upload a contract or an invoice to begin.
        </p>
      )}
      {docs.data && docs.data.length > 0 && (
        <table className="w-full overflow-hidden rounded-lg bg-white text-left text-sm shadow">
          <thead className="bg-slate-100 text-slate-600">
            <tr>
              <th className="px-3 py-2">File</th>
              <th className="px-3 py-2">Type</th>
              <th className="px-3 py-2">Status</th>
              <th className="px-3 py-2">Pages</th>
            </tr>
          </thead>
          <tbody>
            {docs.data.map((d) => (
              <tr key={d.id} className="border-t border-slate-100">
                <td className="px-3 py-2">{d.filename}</td>
                <td className="px-3 py-2">{d.kind}</td>
                <td className="px-3 py-2">
                  <StatusBadge status={d.status} />
                  {d.status === "failed" && d.error && (
                    <p className="mt-1 text-xs text-red-700">{d.error}</p>
                  )}
                </td>
                <td className="px-3 py-2">{d.page_count ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
