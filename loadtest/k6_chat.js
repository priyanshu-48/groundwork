// Chat overhead with the deterministic demo model (AI_PROVIDER=fake): measures our code (auth,
// limits, search, SSE, persistence), not Gemini. Two modes:
//   MODE=load   each VU has its own org; run the stack with high CHAT_RATE_LIMIT_PER_MIN and
//               SIGNUP_RATE_LIMIT_PER_MIN
//   MODE=limit  one org sends LIMIT+3 requests; the stack runs with CHAT_RATE_LIMIT_PER_MIN=LIMIT
//               and the extra requests must be 429 with Retry-After
// k6 buffers the stream: http_req_waiting is time-to-first-byte, http_req_duration the total.
import http from "k6/http";
import { check } from "k6";

const BASE = __ENV.BASE_URL || "http://host.docker.internal:8000";
const MODE = __ENV.MODE || "load";
const LIMIT = Number(__ENV.LIMIT || 20);
const VUS = Number(__ENV.VUS || 10);
const PW = "k6-load-test-password";
const JSON_H = { "Content-Type": "application/json" };

export const options =
  MODE === "limit"
    ? { vus: 1, iterations: 1 }
    : {
        scenarios: {
          chat: {
            executor: "ramping-vus",
            startVUs: 1,
            stages: [
              { target: VUS, duration: "10s" },
              { target: VUS, duration: "30s" },
            ],
          },
        },
        thresholds: { http_req_failed: ["rate<0.01"], checks: ["rate>0.99"] },
        summaryTrendStats: ["avg", "med", "p(90)", "p(95)", "p(99)", "max"],
      };

function newOrg() {
  const email = `k6-${__VU}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}@example.com`;
  const body = JSON.stringify({ org_name: "k6", email, password: PW });
  const r = http.post(`${BASE}/auth/signup`, body, { headers: JSON_H });
  if (r.status !== 201) throw new Error(`signup failed: ${r.status} ${r.body}`);
  const headers = { ...JSON_H, Authorization: `Bearer ${r.json("access_token")}` };
  const c = http.post(`${BASE}/conversations`, "{}", { headers });
  return { headers, conv: c.json("id") };
}

function ask(o) {
  const body = JSON.stringify({ content: "What are the payment terms?" });
  return http.post(`${BASE}/chat/${o.conv}/messages`, body, { headers: o.headers });
}

let org; // one org per VU, created on its first iteration

export default function () {
  if (MODE === "limit") {
    const o = newOrg();
    const codes = [];
    let last;
    for (let i = 0; i < LIMIT + 3; i++) {
      last = ask(o);
      codes.push(last.status);
    }
    check(null, {
      "first LIMIT requests succeed": () => codes.slice(0, LIMIT).every((c) => c === 200),
      "the rest are 429": () => codes.slice(LIMIT).every((c) => c === 429),
      "429 has Retry-After": () => Number(last.headers["Retry-After"]) >= 1,
    });
    return;
  }
  org = org || newOrg();
  const r = ask(org);
  check(r, {
    "200": (x) => x.status === 200,
    "stream ends with done": (x) => x.body.includes("event: done"),
  });
}
