import { defineConfig } from "@playwright/test";

// The e2e test needs the backend on :8000 running with AI_PROVIDER=fake (deterministic demo model):
//   AI_PROVIDER=fake docker compose up -d --build postgres s3 s3-init api worker
// The Vite dev server is started here and proxies /api to it.
export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  retries: 0,
  use: { baseURL: "http://localhost:5173", trace: "retain-on-failure" },
  webServer: {
    command: "npm run dev",
    url: "http://localhost:5173",
    reuseExistingServer: true,
    timeout: 30_000,
  },
});
