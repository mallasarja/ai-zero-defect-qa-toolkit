# IO-136500 — PR-Focused Backend Tests (Derived from PR 682: Context3)

Source PR(s): https://github.com/celigo/gptverse/pull/682

Note: Where AC linkage is unclear from the story, tests are tagged PR-IMPACT.

## Changed Functions/Modules & Integration Points
- **Area:** `/v1/gptverse/knowledge-base/answer` request handling, context resolution, streaming frames composer
- **Integration:** Context resolver service, Knowledge Base backend, feature flag `context_aware`, observability (logs/metrics/traces)
- **Risk Topics:** stream envelope format, suggestions/links blocks, URL→context fallback, retries on KB calls, thread_id idempotency

---

## Functional (Changed Logic)
- **Test Case ID:** IO-136500-PR-FUNC-001
- **Title/Description:** Ensure updated stream composer still appends Suggestions and Links blocks in correct order
- **Preconditions:** Service running; consumer parser available
- **Test Steps:**
  - POST answer with `stream=true` and realistic payload
  - Collect full stream until termination
  - Locate `$$$$---SUGGESTIONS---$$$$` followed by `$$$$---LINK---$$$$`
  - JSON-parse both blocks
- **Test Data:** Same profile as Jira suite FUNC-001
- **Expected Result:** Order preserved (Suggestions then Links); both blocks schema-valid
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Regression, Functional, Stream, PR-IMPACT
- **Test Type:** Functional
- **AC Tag(s):** AC-2

- **Test Case ID:** IO-136500-PR-FUNC-002
- **Title/Description:** URL-derived context fallback engages only when `context_value` is null/empty
- **Preconditions:** Resolver healthy
- **Test Steps:**
  - Case A: `context_value=null` → expect resolver call
  - Case B: `context_value="Already Extracted Context"` → no resolver call
  - Verify logs/trace spans for resolver usage
- **Test Data:** Two payloads A/B differing only in `context_value`
- **Expected Result:** A uses resolver; B skips; outputs align with page scope
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Functional, Context
- **Test Type:** Functional
- **AC Tag(s):** AC-1

---

## API Contract & Schema/Versioning Guards
- **Test Case ID:** IO-136500-PR-API-001
- **Title/Description:** Response stream envelope and frame schema unchanged post-change
- **Preconditions:** OpenAPI/contract snapshot available
- **Test Steps:**
  - Compare live response to stored contract (shape of frames, terminator, headers)
- **Test Data:** `stream=true`
- **Expected Result:** No contract drift; headers (`content-type`, `x-request-id`) intact
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** API, Contract, Regression
- **Test Type:** API
- **AC Tag(s):** AC-2

- **Test Case ID:** IO-136500-PR-API-002
- **Title/Description:** Reject unknown/experimental fields with 400 to protect versioning
- **Preconditions:** Validation pipeline enabled
- **Test Steps:**
  - Send payload including `context_version: 999` (unsupported) and `unknown_field: true`
- **Test Data:** Modified payload
- **Expected Result:** 400 with explicit validation errors; no silent acceptance
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** API, Contract, PR-IMPACT
- **Test Type:** API
- **AC Tag(s):** AC-2

---

## Retry/Backoff/Idempotency Changes
- **Test Case ID:** IO-136500-PR-SREL-001
- **Title/Description:** Updated KB call path uses exponential backoff with jitter; bounded retries
- **Preconditions:** Fault injection (20% 5xx/timeouts)
- **Test Steps:**
  - Run 100 calls; trace retries count and spacing
  - Validate max retries, backoff pattern, and jitter present
- **Test Data:** Fault profile enabled
- **Expected Result:** Retries <= configured max; intervals grow; success rate improves; no thundering herd
- **Actual Result:**
- **Status:**
- **Postconditions:** Disable faults
- **Tags/Labels:** Reliability, Retry
- **Test Type:** Recovery
- **AC Tag(s):** AC-2

- **Test Case ID:** IO-136500-PR-DATA-001
- **Title/Description:** Idempotency maintained for identical `thread_id` after refactor
- **Preconditions:** Same thread replay
- **Test Steps:**
  - Call twice with identical payload including `thread_id`
  - Diff Suggestions/Links sections and main content
- **Test Data:** `thread_id="thread_stable_001"`
- **Expected Result:** No duplicate blocks; content stable across replays
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Data Integrity, Idempotency
- **Test Type:** Data Integrity
- **AC Tag(s):** AC-2

---

## Performance Regressions on Modified Hot Paths
- **Test Case ID:** IO-136500-PR-PERF-001
- **Title/Description:** Latency guardrail on stream startup after composer changes
- **Preconditions:** Perf env; baseline available
- **Test Steps:**
  - Measure time to first byte (TTFB) for stream over 200 requests
  - Compare to baseline; compute P50/P95 deltas
- **Test Data:** Representative queries
- **Expected Result:** P95 TTFB within +10% of baseline; error rate <1%
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Performance, Regression
- **Test Type:** Performance
- **AC Tag(s):** AC-2

- **Test Case ID:** IO-136500-PR-PERF-002
- **Title/Description:** CPU/memory regression check for context fallback path
- **Preconditions:** APM/metrics enabled
- **Test Steps:**
  - Run 500 calls with `context_value=null`; collect CPU/mem; compare to baseline
- **Test Data:** Fallback payloads
- **Expected Result:** Resource usage within +10% baseline; no leaks
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Performance, Context
- **Test Type:** Performance
- **AC Tag(s):** AC-2

---

## Security Impacts (Scope/Permissions/Secrets)
- **Test Case ID:** IO-136500-PR-SEC-001
- **Title/Description:** RBAC scope unchanged for resolver and KB calls after changes
- **Preconditions:** Roles/scopes configured
- **Test Steps:**
  - Invoke resolver with limited scopes and ensure denial as designed
  - Invoke KB call path and validate allowed scopes
- **Test Data:** Tokens with varied scopes
- **Expected Result:** No scope widening; least-privilege preserved
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Security, AuthZ, PR-IMPACT
- **Test Type:** Security
- **AC Tag(s):** AC-2

- **Test Case ID:** IO-136500-PR-SEC-002
- **Title/Description:** Secrets and PII redaction still effective in new logs emitted by changed code
- **Preconditions:** Log redaction rules active
- **Test Steps:**
  - Send queries with dummy PII; inspect new/modified log lines
- **Test Data:** Email, phone, SSN dummy inputs
- **Expected Result:** No PII or secrets in logs; redaction masks applied
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Security, PII, PR-IMPACT
- **Test Type:** Security
- **AC Tag(s):** AC-2

---

## Error Paths
- **Test Case ID:** IO-136500-PR-ERR-001
- **Title/Description:** Structured error on mid-stream KB failure via updated composer
- **Preconditions:** Fault injection mid-stream
- **Test Steps:**
  - Start streaming; inject KB 5xx mid-way; capture termination
- **Test Data:** Long-running query
- **Expected Result:** Graceful termination frame; structured error; correlation id present
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Error, Observability
- **Test Type:** Error/Observability
- **AC Tag(s):** AC-2

- **Test Case ID:** IO-136500-PR-ERR-002
- **Title/Description:** Resolver unavailability leads to fallback behavior or explicit error (no partial frames)
- **Preconditions:** Resolver down
- **Test Steps:**
  - Request with `context_value=null`; observe behavior
- **Test Data:** Fallback payload
- **Expected Result:** Either clean fallback to default scope or early 503; no partial/silent failures
- **Actual Result:**
- **Status:**
- **Postconditions:** Restore resolver
- **Tags/Labels:** Error, Recovery, PR-IMPACT
- **Test Type:** Error/Recovery
- **AC Tag(s):** AC-2

---

## Compatibility/Versioning
- **Test Case ID:** IO-136500-PR-COMP-001
- **Title/Description:** Behavior stable for clients omitting new/optional fields
- **Preconditions:** N/A
- **Test Steps:**
  - Omit `context_aware`, `context_value`; call API
- **Test Data:** Minimal payload
- **Expected Result:** 200; default behavior; no breaking changes
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Compatibility, Regression
- **Test Type:** Compatibility
- **AC Tag(s):** AC-1, AC-2
