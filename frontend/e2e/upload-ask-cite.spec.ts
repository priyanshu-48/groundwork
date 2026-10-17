import { expect, test } from "@playwright/test";
import { fileURLToPath } from "node:url";

const fixture = fileURLToPath(new URL("./fixtures/net45.pdf", import.meta.url));

// Sign up -> upload a PDF -> wait until it is ingested -> ask -> streamed answer with a citation.
test("upload a document, ask about it, and open the citation", async ({ page }) => {
  const email = `e2e-${Date.now()}@example.com`;

  await page.goto("/");
  await expect(page).toHaveURL(/\/login/);
  await page.getByRole("button", { name: /create a workspace/i }).click();
  await page.getByLabel("Company name").fill("E2E Co");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("a-long-e2e-password");
  await page.getByRole("button", { name: "Create account" }).click();

  await expect(page).toHaveURL(/\/documents/);
  await expect(page.getByText(/Demo mode/)).toBeVisible(); // honest about the fake model

  await page.getByLabel("Upload PDF files").setInputFiles(fixture);
  const row = page.getByRole("row", { name: /net45\.pdf/ });
  await expect(row).toBeVisible();
  await expect(row.getByText("ready")).toBeVisible({ timeout: 45_000 }); // the worker ingests it

  await page.getByRole("link", { name: "Chat" }).click();
  await page.getByLabel("Your question").fill("What are the payment terms?");
  await page.getByRole("button", { name: "Ask" }).click();

  const chip = page.getByRole("button", { name: /Source C1: net45\.pdf, page 1/ });
  await expect(chip).toBeVisible({ timeout: 30_000 });
  await expect(page.getByText(/Net 45/).first()).toBeVisible();

  await chip.click();
  const source = page.getByRole("complementary", { name: "Source C1" });
  await expect(source).toContainText("net45.pdf");
  await expect(source).toContainText("page 1");

  await page.getByText(/^Steps \(1\)$/).click();
  await expect(page.getByText("search_documents")).toBeVisible();
  await expect(page).toHaveURL(/\/chat\/[0-9a-f-]{36}/); // the conversation was created and kept
});
