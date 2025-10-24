# IO-136500 — AI (BE) vs Manual (BE) Comparison and Verdict

## Executive Summary
- Verdict: AI stronger
- Why: Better AC traceability, deeper failure/reliability and security coverage, PR-impact areas covered.
- Quality Bar: AI Pass; Manual Fail (insufficient BE realism and AC traceability)

## Scores
- AI: AC 8/10, Service realism 8/10, Negative/Edge 8/10 → 24/30 (80.0%)
- Manual: AC 4/10, Service realism 5/10, Negative/Edge 4/10 → 13/30 (43.3%)

## Acceptance Criteria Coverage Matrix
- AC-1 (Context resolution via URL/context_value): AI Fully; Manual Partial
- AC-2 (Streaming + suggestions/links + schema/headers): AI Fully; Manual Partial
- PR-IMPACT (composer/refactor reliability & perf): AI Fully; Manual Not Covered

## Mapping (Manual ↔ AI)
- Manual CSV-based scenarios → AI FUNC-001/002 (Exact 0.92)
- Manual similarity to AI reliability/perf/security: Unmapped (<0.4)

## Gaps in Manual (with risk)
- High: Retry/backoff/jitter and mid-stream failure handling → Covered by AI PR-SREL-001, PR-ERR-001
- High: API contract/versioning guards and unknown-field rejection → Covered by AI PR-API-002
- Medium: Idempotency on `thread_id` and duplicate suppression → Covered by AI PR-DATA-001
- Medium: Perf guardrails on TTFB and fallback CPU/memory → Covered by AI PR-PERF-001/002
- Medium: RBAC scope and PII redaction verification → Covered by AI PR-SEC-001/002

## Gaps in AI (with BE skeletons)
- High: Dead-letter/poison queue policy for resolver events
  - Test Case ID: IO-136500-AI-GAP-REL-001
  - Preconditions: Resolver publishes `context.resolve`; DLQ configured
  - Test Steps: Publish invalid message → observe DLQ; republish fixed → observe recovery
  - Test Data: malformed message { url:"", trace_id:"t1" }
  - Expected: Message routed to DLQ; metrics increment; alert fired; successful replay clears DLQ
  - Tags/Type: Reliability, Queues; Recovery; PR-IMPACT
- Medium: Circuit breaker half-open evaluation on KB 5xx bursts
  - Test Case ID: IO-136500-AI-GAP-REL-002
  - Preconditions: Breaker thresholds configured
  - Test Steps: Inject 5xx burst → open; wait window → probe; verify close on success
  - Expected: State transitions OPEN→HALF_OPEN→CLOSED; bounded errors; logs/traces
  - Tags/Type: Reliability; Recovery; PR-IMPACT

## Parity Checks
- API contract: Keep `data:` envelope and terminator stable (AI PR-API-001)
- Versioning: Reject unknown fields (AI PR-API-002)
- Feature flag: `context_aware` off-state graceful behavior (AI COMP-001)

## Reliability Matrix
- Retries/backoff/jitter: Present (AI PR-SREL-001)
- Circuit breaker: Add (AI GAP REL-002)
- DLQ/poison: Add (AI GAP REL-001)
- Duplicate handling/idempotency: Present (AI PR-DATA-001)

## Quality Checks
- AI categories: Functional(2), Regression(2), Negative(2), Integration(2), API(2), Performance(2), Security(2), Data Integrity(1), Reliability/Recovery(2), Compatibility(1), Error/Observability(2)
- Manual categories: Mostly functional/UI-like; limited BE reliability/security
- Service realism: AI ~80%; Manual ~50%
- Data realism: AI ~75%; Manual ~40%
- Duplicates: Manual contains overlapping UI-context validations

## Top-10 Risk-Prioritized Adds
1) DLQ handling for resolver (High)
2) Circuit breaker half-open probe (High)
3) Unknown-field/version guard (High)
4) Mid-stream failure termination frame (High)
5) TTFB regression guardrail (High)
6) CPU/memory regression on fallback path (Medium)
7) Idempotent `thread_id` replay (Medium)
8) RBAC scope verification (Medium)
9) PII log redaction checks (Medium)
10) Resolver down fallback vs 503 behavior (Medium)

## Refined Backend Prompt (Essentials)
- Require per-AC tags (AC-1/AC-2) or PR-IMPACT
- Enforce BE-executable verbs: publish to topic, inject 5xx/timeout, throttle QPS, SIGTERM pod, rotate key, mutate headers
- Include: idempotency (thread_id), ordering, retries/backoff/jitter, circuit breaker, DLQ/poison, transactional integrity, API error codes, perf SLAs (TTFB/P95), RBAC scope checks, PII/secrets redaction

## Decision
- AI suite passes the BE Quality Bar; Manual does not. AI recommended as baseline; augment with listed gaps.

---
Update Note
- Normalized IO-style BE suite saved at `Innovative Quality Initiatives-AI/jira_stories/IO-136500-testcases_v4.md`. Use this for re-evaluation.
