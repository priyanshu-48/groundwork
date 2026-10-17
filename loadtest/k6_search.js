// POST /search under load. Two phases, reported separately because they measure different things:
//   cold: 40 unique queries at ~1 req/s  -> every request pays a real query-embedding call
//   warm: the same 40 queries repeated at TARGET_RPS -> served from the query-embedding cache
// Needs a stack with the eval corpus loaded and a high SEARCH_RATE_LIMIT_PER_MIN (the default
// 60/min per org would throttle the warm phase). See loadtest/README.md for the exact command.
import http from "k6/http";
import { check } from "k6";
import exec from "k6/execution";

const QUERIES = JSON.parse(open("./queries.json"));
const BASE = __ENV.BASE_URL || "http://host.docker.internal:8000";
const TARGET_RPS = Number(__ENV.TARGET_RPS || 20);

export const options = {
  scenarios: {
    cold: {
      executor: "constant-arrival-rate",
      rate: 1,
      timeUnit: "1s",
      duration: "40s",
      preAllocatedVUs: 2,
      exec: "cold",
    },
    warm: {
      executor: "ramping-arrival-rate",
      startTime: "45s",
      startRate: 1,
      timeUnit: "1s",
      preAllocatedVUs: 20,
      maxVUs: 50,
      exec: "warm",
      stages: [
        { target: TARGET_RPS, duration: "10s" },
        { target: TARGET_RPS, duration: "30s" },
      ],
    },
  },
  thresholds: {
    "http_req_failed{scenario:warm}": ["rate<0.01"],
    "http_req_failed{scenario:cold}": ["rate<0.01"],
    // Always declared so k6 prints each phase's latency; the budgets are set from measurements.
    "http_req_duration{scenario:warm}": [`p(95)<${__ENV.WARM_P95_MS || 100000}`],
    "http_req_duration{scenario:cold}": [`p(95)<${__ENV.COLD_P95_MS || 100000}`],
  },
  summaryTrendStats: ["avg", "med", "p(90)", "p(95)", "p(99)", "max"],
};

export function setup() {
  const body = JSON.stringify({
    email: __ENV.EVAL_EMAIL || "eval@example.com",
    password: __ENV.EVAL_PASSWORD,
  });
  const r = http.post(`${BASE}/auth/login`, body, { headers: { "Content-Type": "application/json" } });
  if (r.status !== 200) throw new Error(`login failed: ${r.status}`);
  return { token: r.json("access_token") };
}

function search(data, iter) {
  // RUN_ID keeps these queries out of any cache left over from an earlier run
  const query = `${QUERIES[iter % QUERIES.length]} ${__ENV.RUN_ID || ""}`.trim();
  const r = http.post(`${BASE}/search`, JSON.stringify({ query, top_k: 5 }), {
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${data.token}` },
  });
  check(r, { "200": (x) => x.status === 200, "has hits": (x) => x.json("hits").length > 0 });
}

export function cold(data) {
  search(data, exec.scenario.iterationInTest);
}

export function warm(data) {
  search(data, exec.scenario.iterationInTest);
}
