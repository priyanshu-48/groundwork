import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { Citation } from "../api/types";
import { CitedText, splitCitations } from "./CitedText";

const cite = (ref: string, filename = "acme.pdf", page = 2): Citation => ({
  ref,
  chunk_id: `chunk-${ref}`,
  document_id: "doc",
  filename,
  page,
  snippet: "Net 45 applies",
});

describe("splitCitations", () => {
  it("splits text and markers, including comma lists", () => {
    expect(splitCitations("Net 45 [C1] and more [C2, C3].")).toEqual([
      { kind: "text", value: "Net 45 " },
      { kind: "refs", refs: ["C1"] },
      { kind: "text", value: " and more " },
      { kind: "refs", refs: ["C2", "C3"] },
      { kind: "text", value: "." },
    ]);
  });

  it("treats adjacent markers as separate groups and leaves ordinary brackets alone", () => {
    expect(splitCitations("[C1][C2]")).toEqual([
      { kind: "refs", refs: ["C1"] },
      { kind: "refs", refs: ["C2"] },
    ]);
    expect(splitCitations("see [notes] and [c1] and [C]")).toEqual([
      { kind: "text", value: "see [notes] and [c1] and [C]" },
    ]);
  });

  it("returns a single text segment when there are no markers", () => {
    expect(splitCitations("plain")).toEqual([{ kind: "text", value: "plain" }]);
    expect(splitCitations("")).toEqual([]);
  });
});

describe("CitedText", () => {
  const setup = (text: string, citations: Citation[], selected: string | null = null) => {
    const onSelect = vi.fn();
    const view = render(<CitedText text={text} citations={citations} selected={selected} onSelect={onSelect} />);
    return { onSelect, ...view };
  };

  it("turns a known marker into an accessible button that reports its ref", async () => {
    const { onSelect } = setup("Net 45 [C1].", [cite("C1")]);
    const chip = screen.getByRole("button", { name: "Source C1: acme.pdf, page 2" });
    expect(chip).toHaveAttribute("aria-expanded", "false");
    await userEvent.click(chip);
    expect(onSelect).toHaveBeenCalledWith("C1");
  });

  it("clicking the open chip again closes it", async () => {
    const { onSelect } = setup("x [C1]", [cite("C1")], "C1");
    const chip = screen.getByRole("button", { name: /Source C1/ });
    expect(chip).toHaveAttribute("aria-expanded", "true");
    await userEvent.click(chip);
    expect(onSelect).toHaveBeenCalledWith(null);
  });

  it("a marker without a matching citation stays plain text", () => {
    setup("Maybe [C9] and [C1]", [cite("C1")]);
    expect(screen.getAllByRole("button")).toHaveLength(1);
    expect(screen.getByText(/\[C9\]/)).toBeInTheDocument();
  });

  it("renders comma lists as one chip per known ref", () => {
    setup("Both [C1, C2]", [cite("C1"), cite("C2", "b.pdf", 5)]);
    expect(screen.getByRole("button", { name: "Source C2: b.pdf, page 5" })).toBeInTheDocument();
    expect(screen.getAllByRole("button")).toHaveLength(2);
  });

  it("never interprets model output as HTML", () => {
    const evil = '<img src=x onerror="alert(1)"> <b>bold</b> [C1]';
    const { container } = setup(evil, [cite("C1")]);
    expect(container.querySelector("img")).toBeNull();
    expect(container.querySelector("b")).toBeNull();
    expect(container.textContent).toContain('<img src=x onerror="alert(1)">');
  });
});
