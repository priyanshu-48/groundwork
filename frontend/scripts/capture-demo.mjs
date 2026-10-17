// Captures the frames for docs/demo.gif from a running deployment's demo workspace.
//   node scripts/capture-demo.mjs https://<host> <output-dir>
// Uses 3 questions of the demo's daily budget. Then, from backend/: uv run --with pillow python ../frontend/scripts/make_demo_gif.py <output-dir> ../docs/demo.gif
import { chromium } from "@playwright/test";
import { mkdirSync } from "node:fs";

const [base, out] = process.argv.slice(2);
if (!base || !out) throw new Error("usage: node scripts/capture-demo.mjs <base-url> <output-dir>");
mkdirSync(out, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1100, height: 700 } });
let n = 0;
const shot = async (name) => page.screenshot({ path: `${out}/${String(++n).padStart(2, "0")}-${name}.png` });
const slow = { timeout: 120_000 };

await page.goto(base);
await page.getByRole("button", { name: /try the demo/i }).waitFor();
await shot("login");

await page.getByRole("button", { name: /try the demo/i }).click();
await page.getByRole("row").nth(5).waitFor(slow);
await shot("documents");

await page.getByRole("link", { name: "Chat" }).click();
await page.getByRole("list", { name: "Suggested questions" }).waitFor();
await shot("suggestions");

await page.getByRole("button", { name: /termination notice period in the Kestrel/i }).click();
await page.waitForTimeout(1500);
await shot("working");
const chip = page.getByRole("button", { name: /Source C1/ }).first();
await chip.waitFor(slow);
await page.getByText(/ninety|90/).first().waitFor(slow);
await shot("answer");

await chip.click();
await page.getByRole("complementary", { name: "Source C1" }).waitFor();
await shot("source");

await page.getByText(/^Steps \(/).first().click();
await page.waitForTimeout(500);
await shot("steps");

await page.getByRole("button", { name: "New chat" }).click();
await page.getByRole("button", { name: /Ironbridge Facilities bill us/i }).click();
await page.getByText(/63,382/).first().waitFor(slow);
await page.waitForTimeout(800);
await shot("aggregate");

await page.getByRole("button", { name: "New chat" }).click();
await page.getByRole("button", { name: /net-45 terms billed us the most/i }).click();
await page.getByText(/Northwind Labs/).first().waitFor(slow);
await page.waitForTimeout(800);
await shot("multihop");

await browser.close();
console.log(`saved ${n} frames to ${out}`);
