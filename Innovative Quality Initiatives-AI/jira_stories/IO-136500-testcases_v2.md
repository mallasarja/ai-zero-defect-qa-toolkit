# IO-136500 — Backend Test Suite v2 (Refined)

Note: Each case includes AC tags (AC-1/AC-2) or PR-IMPACT.

## Functional
- **Test Case ID:** IO-136500-FUNC-001
- **Title/Description:** Context-aware answer using provided `context_value` without resolver
- **Preconditions:** Feature flag `context_aware=true`; resolver healthy
- **Test Steps:**
  - POST `/v1/gptverse/knowledge-base/answer` with `context_value="Already Extracted Context"`, `stream=true`, `return_sources=true`
  - Validate 200 and streaming start
- **Test Data:** Headers `Authorization`, `x-request-id`; Body with query, url, context_aware=true, context_value, thread_id
- **Expected Result:** Stream frames emitted; Suggestions and Links blocks appended; no resolver span
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Functional, API
- **Test Type:** Functional
- **AC Tag(s):** AC-1, AC-2

- **Test Case ID:** IO-136500-FUNC-002
- **Title/Description:** Fallback to URL-derived context when `context_value=null`
- **Preconditions:** Resolver reachable
- **Test Steps:**
  - POST with `context_value=null`
  - Verify resolver span and resolved scope tag
- **Test Data:** Body with null context_value
- **Expected Result:** Answer scoped to page inferred from URL
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Functional, Context
- **Test Type:** Functional
- **AC Tag(s):** AC-1

## Regression
- **Test Case ID:** IO-136500-REG-001
- **Title/Description:** Preserve `data:` stream envelope and terminator
- **Preconditions:** Contract snapshot
- **Test Steps:**
  - Capture full stream and compare to envelope spec
- **Test Data:** stream=true
- **Expected Result:** Envelope unchanged; consumer parsers pass
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Regression, Contract
- **Test Type:** Regression
- **AC Tag(s):** AC-2

- **Test Case ID:** IO-136500-REG-002
- **Title/Description:** Suggestions precede Links; schemas valid
- **Preconditions:** N/A
- **Test Steps:**
  - Extract blocks; JSON-validate
- **Test Data:** As in FUNC-001
- **Expected Result:** Order correct; schema valid
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Regression, Stream
- **Test Type:** Regression
- **AC Tag(s):** AC-2

## Negative
- **Test Case ID:** IO-136500-NEG-001
- **Title/Description:** 400 on missing query; explicit validation errors
- **Preconditions:** N/A
- **Test Steps:**
  - POST with `query:""`
- **Test Data:** Minimal body
- **Expected Result:** 400 `{ code:"BAD_REQUEST", details:[...] }`; audit log record
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Negative, Validation
- **Test Type:** Negative
- **AC Tag(s):** AC-2

- **Test Case ID:** IO-136500-NEG-002
- **Title/Description:** 401 on expired token; no data leakage
- **Preconditions:** Expired token
- **Test Steps:**
  - POST with invalid Authorization
- **Test Data:** `Authorization: Bearer invalid`
- **Expected Result:** 401 with standard error; no frames
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Security, Negative
- **Test Type:** Negative
- **AC Tag(s):** AC-2

## Integration
- **Test Case ID:** IO-136500-INT-001
- **Title/Description:** URL→resolver→answer chaining with correlation IDs
- **Preconditions:** Resolver + KB online
- **Test Steps:**
  - Publish URL to `context.resolve`; receive scope
  - Call answer with scope; check correlation propagation across services
- **Test Data:** URL, thread_id
- **Expected Result:** Trace shows linked spans; end-to-end success
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Integration, Queues
- **Test Type:** Integration
- **AC Tag(s):** AC-1

- **Test Case ID:** IO-136500-INT-002
- **Title/Description:** `ui_image` is transient; not persisted
- **Preconditions:** Logs accessible
- **Test Steps:**
  - Send base64 image; verify no persistence; redaction where logged
- **Test Data:** base64 image
- **Expected Result:** Transient handling only; no PII retention
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Integration, PII
- **Test Type:** Integration
- **AC Tag(s):** AC-2

## API Contract
- **Test Case ID:** IO-136500-API-001
- **Title/Description:** Unknown field and invalid `context_version` rejected
- **Preconditions:** Validation enabled
- **Test Steps:**
  - Add `unknown_field:true`, `context_version:999`
- **Test Data:** Modified body
- **Expected Result:** 400 with explicit errors; no silent forward-compat acceptance
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** API, Versioning
- **Test Type:** API
- **AC Tag(s):** AC-2, PR-IMPACT

- **Test Case ID:** IO-136500-API-002
- **Title/Description:** Headers present: `content-type`, `x-request-id`; schema conformance
- **Preconditions:** Spec available
- **Test Steps:**
  - Validate request/response against OpenAPI; check headers
- **Test Data:** As in FUNC-001
- **Expected Result:** Conforms; errors throw correct codes
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** API, Contract
- **Test Type:** API
- **AC Tag(s):** AC-2

## Performance/Stress/Load
- **Test Case ID:** IO-136500-PERF-001
- **Title/Description:** TTFB P95 within +10% baseline on stream start
- **Preconditions:** Baseline available
- **Test Steps:**
  - Run 200 requests; measure TTFB; compute deltas
- **Test Data:** Representative queries
- **Expected Result:** P95 within SLA; error<1%
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Performance, Regression
- **Test Type:** Performance
- **AC Tag(s):** AC-2, PR-IMPACT

- **Test Case ID:** IO-136500-PERF-002
- **Title/Description:** CPU/memory regression check on fallback path
- **Preconditions:** APM enabled
- **Test Steps:**
  - 500 calls with `context_value=null`; record CPU/mem vs baseline
- **Test Data:** Fallback payloads
- **Expected Result:** Within +10% baseline; no leaks
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Performance, Context
- **Test Type:** Performance
- **AC Tag(s):** AC-2, PR-IMPACT

## Security
- **Test Case ID:** IO-136500-SEC-001
- **Title/Description:** RBAC scopes enforced for resolver and KB
- **Preconditions:** Roles/scopes present
- **Test Steps:**
  - Call with limited scopes; verify 403/404 where applicable
- **Test Data:** Tokens with varied scopes
- **Expected Result:** Least-privilege preserved; no scope widening
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Security, AuthZ
- **Test Type:** Security
- **AC Tag(s):** AC-2

- **Test Case ID:** IO-136500-SEC-002
- **Title/Description:** PII/secrets redaction in logs for new code paths
- **Preconditions:** Redaction rules active
- **Test Steps:**
  - Inject dummy PII; scan logs for leakage
- **Test Data:** Email, SSN dummy
- **Expected Result:** Redacted; no leakage
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Security, PII
- **Test Type:** Security
- **AC Tag(s):** AC-2, PR-IMPACT

## Data Integrity
- **Test Case ID:** IO-136500-DATA-001
- **Title/Description:** Idempotent replay on same `thread_id`
- **Preconditions:** Same thread replay scenario
- **Test Steps:**
  - Repeat identical request; diff frames and blocks
- **Test Data:** Fixed `thread_id`
- **Expected Result:** No duplicates; stable outputs
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Data Integrity, Idempotency
- **Test Type:** Data Integrity
- **AC Tag(s):** AC-2

## Reliability/Recovery/Redundancy/Race
- **Test Case ID:** IO-136500-SREL-001
- **Title/Description:** Exponential backoff with jitter on KB 5xx/timeout
- **Preconditions:** Fault injection 20%
- **Test Steps:**
  - Inject 5xx/timeouts; observe retry schedule; verify bounds
- **Test Data:** Fault profile
- **Expected Result:** Bounded retries; jitter; improved success; no herd
- **Actual Result:**
- **Status:**
- **Postconditions:** Disable faults
- **Tags/Labels:** Reliability, Retry
- **Test Type:** Recovery
- **AC Tag(s):** AC-2

- **Test Case ID:** IO-136500-SREL-002
- **Title/Description:** Circuit breaker OPEN→HALF_OPEN→CLOSED on KB failure bursts
- **Preconditions:** Breaker thresholds configured
- **Test Steps:**
  - Trigger error burst; verify OPEN; wait; probe; verify close
- **Test Data:** Burst profile
- **Expected Result:** Correct state transitions; bounded errors; alerts
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Reliability, CircuitBreaker
- **Test Type:** Recovery
- **AC Tag(s):** PR-IMPACT

- **Test Case ID:** IO-136500-SREL-003
- **Title/Description:** DLQ/poison queue on invalid resolver messages + replay
- **Preconditions:** DLQ configured
- **Test Steps:**
  - Publish malformed `context.resolve`; confirm DLQ; fix and replay
- **Test Data:** `{ url:"", trace_id:"t1" }`
- **Expected Result:** Routed to DLQ; metrics/alerts; successful replay cleared
- **Actual Result:**
- **Status:**
- **Postconditions:** Clear DLQ
- **Tags/Labels:** Reliability, Queues
- **Test Type:** Recovery
- **AC Tag(s):** PR-IMPACT

## Compatibility
- **Test Case ID:** IO-136500-COMP-001
- **Title/Description:** Clients omitting new/optional fields still succeed
- **Preconditions:** N/A
- **Test Steps:**
  - Omit `context_aware`, `context_value`
- **Test Data:** Minimal body
- **Expected Result:** 200; default behavior preserved
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Compatibility
- **Test Type:** Compatibility
- **AC Tag(s):** AC-1, AC-2

## Error/Observability
- **Test Case ID:** IO-136500-ERR-001
- **Title/Description:** Mid-stream KB failure yields structured termination + alert
- **Preconditions:** Fault injection mid-stream; alerts configured
- **Test Steps:**
  - Start stream; inject KB 5xx; capture termination frame; check alert
- **Test Data:** Long-running query
- **Expected Result:** Structured error with correlation id; alert fired; trace spans marked
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Error, Observability
- **Test Type:** Error/Observability
- **AC Tag(s):** AC-2, PR-IMPACT

## Migration/Flags
- **Test Case ID:** IO-136500-FF-001
- **Title/Description:** Feature flag off-state graceful degradation and rollback
- **Preconditions:** Flag control available
- **Test Steps:**
  - Turn `context_aware` off; validate degraded behavior; roll back on
- **Test Data:** Flag `context_aware`
- **Expected Result:** No outage; expected off-state behavior
- **Actual Result:**
- **Status:**
- **Postconditions:** Restore flag on
- **Tags/Labels:** Feature Flag, Migration
- **Test Type:** Migration
- **AC Tag(s):** AC-1, AC-2
