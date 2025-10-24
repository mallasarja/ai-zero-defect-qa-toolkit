# IO-136500 — Backend Test Suite (Normalized IO Style v4)

Global Preconditions
- Feature flag: context_aware=true unless specified
- Services healthy: context resolver, knowledge-base (KB), API gateway
- Observability on: logs, metrics, traces, alerts

## Functional
- **Test Case ID:** IO-136500-FUNC-001
- **Title/Description:** Context-aware answer when `context_value` provided (no resolver dependency)
- **Preconditions:** Flag on; auth token valid
- **Test Steps:**
  - Call POST /v1/gptverse/knowledge-base/answer with context_value="Already Extracted Context", stream=true, return_sources=true
  - Check dashboard/logs for request accepted → Inspect HTTP payload (stream frames)
- **Test Data:** Headers Authorization, x-request-id; Body {query, url, context_aware:true, context_value, thread_id}
- **Expected Result:** 2xx; stream frames valid; Suggestions precede Links; no resolver span
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Functional, API
- **Test Type:** Functional
- **AC Tag(s):** AC-1, AC-2

- **Test Case ID:** IO-136500-FUNC-002
- **Title/Description:** URL-derived context when context_value=null
- **Preconditions:** Resolver reachable
- **Test Steps:**
  - POST with context_value=null → Verify resolver span → Answer generated
- **Test Data:** Body with null context_value
- **Expected Result:** Scoped answer; resolver span traced; 2xx
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Functional, Context
- **Test Type:** Functional
- **AC Tag(s):** AC-1

## Regression
- **Test Case ID:** IO-136500-REG-001
- **Title/Description:** Preserve `data:` envelope and terminator
- **Preconditions:** Contract baseline
- **Test Steps:**
  - Capture stream → Compare to envelope spec
- **Test Data:** stream=true
- **Expected Result:** Format unchanged; consumer compatibility
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Regression, Contract
- **Test Type:** Regression
- **AC Tag(s):** AC-2

- **Test Case ID:** IO-136500-REG-002
- **Title/Description:** Suggestions then Links; schemas validate
- **Preconditions:** N/A
- **Test Steps:**
  - Extract blocks; JSON schema validate
- **Test Data:** As in FUNC-001
- **Expected Result:** Order and schema correct
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Regression, Stream
- **Test Type:** Regression
- **AC Tag(s):** AC-2

## Negative
- **Test Case ID:** IO-136500-NEG-001
- **Title/Description:** 400 on missing query; structured error
- **Preconditions:** N/A
- **Test Steps:**
  - POST with query=""; Inspect HTTP error payload; Check logs
- **Test Data:** Minimal body
- **Expected Result:** 400 {code:"BAD_REQUEST", details}; audit log event
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Negative, Validation
- **Test Type:** Negative
- **AC Tag(s):** AC-2

- **Test Case ID:** IO-136500-NEG-002
- **Title/Description:** 401 on expired token; no frames begin
- **Preconditions:** Expired token
- **Test Steps:**
  - POST with invalid Authorization
- **Test Data:** Authorization: Bearer invalid
- **Expected Result:** 401; no stream; security audit present
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Security, Negative
- **Test Type:** Negative
- **AC Tag(s):** AC-2

## Integration
- **Test Case ID:** IO-136500-INT-001
- **Title/Description:** URL→resolver→answer trace with correlation IDs
- **Preconditions:** Resolver + KB online
- **Test Steps:**
  - Publish URL to context.resolve; obtain scope → POST answer with scope → Validate linked spans
- **Test Data:** url, thread_id
- **Expected Result:** Spans linked across services; success path
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Integration, Queues
- **Test Type:** Integration
- **AC Tag(s):** AC-1

- **Test Case ID:** IO-136500-INT-002
- **Title/Description:** `ui_image` handled transiently; no persistence/PII leak
- **Preconditions:** Logs accessible
- **Test Steps:**
  - Send base64 image → Search logs/storage for retention
- **Test Data:** base64 image
- **Expected Result:** No persistence; redaction applied
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Integration, PII
- **Test Type:** Integration
- **AC Tag(s):** AC-2

## API Contract
- **Test Case ID:** IO-136500-API-001
- **Title/Description:** Reject unknown fields and invalid context_version
- **Preconditions:** Validation on
- **Test Steps:**
  - Add unknown_field and context_version=999 → POST
- **Test Data:** Modified body
- **Expected Result:** 400; explicit field errors; no forward-compat silently accepted
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** API, Versioning
- **Test Type:** API
- **AC Tag(s):** AC-2, PR-IMPACT

- **Test Case ID:** IO-136500-API-002
- **Title/Description:** Required headers set; schema conformance
- **Preconditions:** Spec available
- **Test Steps:**
  - Validate against OpenAPI; check content-type, x-request-id
- **Test Data:** As in FUNC-001
- **Expected Result:** 2xx; schema valid; correct error codes
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** API, Contract
- **Test Type:** API
- **AC Tag(s):** AC-2

## Performance/Stress/Load
- **Test Case ID:** IO-136500-PERF-001
- **Title/Description:** TTFB P95 within SLA on stream start
- **Preconditions:** Baseline recorded
- **Test Steps:**
  - Run 200 requests; measure TTFB and error rate
- **Test Data:** Query mix; context_aware=true
- **Expected Result:** P95 within SLA; error<1%
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Performance, Regression
- **Test Type:** Performance
- **AC Tag(s):** AC-2, PR-IMPACT

- **Test Case ID:** IO-136500-PERF-002
- **Title/Description:** Fallback path CPU/memory regression guard
- **Preconditions:** APM enabled
- **Test Steps:**
  - 500 calls with context_value=null; profile CPU/mem
- **Test Data:** Fallback payloads
- **Expected Result:** ≤ +10% baseline; no leaks
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Performance, Context
- **Test Type:** Performance
- **AC Tag(s):** AC-2, PR-IMPACT

## Security
- **Test Case ID:** IO-136500-SEC-001
- **Title/Description:** Enforce RBAC scopes for resolver/KB
- **Preconditions:** Roles/scopes defined
- **Test Steps:**
  - Call endpoints with limited scopes → expect denial
- **Test Data:** Scoped tokens
- **Expected Result:** Proper 403/404; no scope widening
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Security, AuthZ
- **Test Type:** Security
- **AC Tag(s):** AC-2

- **Test Case ID:** IO-136500-SEC-002
- **Title/Description:** PII/secrets redaction in new code paths
- **Preconditions:** Redaction rules active
- **Test Steps:**
  - Inject dummy PII; scan logs
- **Test Data:** Email, SSN dummy
- **Expected Result:** Fully redacted; no leakage
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Security, PII
- **Test Type:** Security
- **AC Tag(s):** AC-2, PR-IMPACT

## Data Integrity
- **Test Case ID:** IO-136500-DATA-001
- **Title/Description:** Idempotent replay on same thread_id
- **Preconditions:** Same thread replay scenario
- **Test Steps:**
  - Replay identical request; diff frames/blocks
- **Test Data:** Fixed thread_id
- **Expected Result:** No duplicates; consistent outputs
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Data Integrity, Idempotency
- **Test Type:** Data Integrity
- **AC Tag(s):** AC-2

## Reliability/Recovery/Redundancy/Race
- **Test Case ID:** IO-136500-SREL-001
- **Title/Description:** Retry with exponential backoff + jitter on KB 5xx/timeout
- **Preconditions:** Fault injection 20%
- **Test Steps:**
  - Inject intermittent 5xx/timeouts → observe retry schedule and bounds
- **Test Data:** Fault profile
- **Expected Result:** Bounded retries; jitter applied; breaker not flapping
- **Actual Result:**
- **Status:**
- **Postconditions:** Disable faults
- **Tags/Labels:** Reliability, Retry
- **Test Type:** Recovery
- **AC Tag(s):** AC-2

- **Test Case ID:** IO-136500-SREL-002
- **Title/Description:** Circuit breaker transitions OPEN→HALF_OPEN→CLOSED under failure bursts
- **Preconditions:** Breaker thresholds configured
- **Test Steps:**
  - Trigger error burst; verify OPEN; probe; verify close
- **Test Data:** Burst profile
- **Expected Result:** Correct transitions; alerts emitted
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Reliability, CircuitBreaker
- **Test Type:** Recovery
- **AC Tag(s):** PR-IMPACT

- **Test Case ID:** IO-136500-SREL-003
- **Title/Description:** DLQ/poison queue routing and replay for malformed resolver messages
- **Preconditions:** DLQ configured
- **Test Steps:**
  - Publish malformed context.resolve → confirm DLQ → fix and replay
- **Test Data:** { url:"", trace_id:"t1" }
- **Expected Result:** DLQ routed; alert; replay clears
- **Actual Result:**
- **Status:**
- **Postconditions:** Clear DLQ
- **Tags/Labels:** Reliability, Queues
- **Test Type:** Recovery
- **AC Tag(s):** PR-IMPACT

## Compatibility
- **Test Case ID:** IO-136500-COMP-001
- **Title/Description:** Backward compatibility for clients omitting context fields
- **Preconditions:** None
- **Test Steps:**
  - Omit context_aware/context_value; call API
- **Test Data:** Minimal body
- **Expected Result:** 2xx; default behavior preserved
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** Compatibility
- **Test Type:** Compatibility
- **AC Tag(s):** AC-1, AC-2

## Error/Observability
- **Test Case ID:** IO-136500-ERR-001
- **Title/Description:** Mid-stream KB failure → structured termination + alert
- **Preconditions:** Fault injection mid-stream; alerts configured
- **Test Steps:**
  - Start stream → inject KB 5xx → capture termination frame → check alert and trace
- **Test Data:** Long-running query
- **Expected Result:** Structured error with correlation ID; alert fired; spans marked error
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
  - Toggle context_aware off → validate degraded behavior → roll back on
- **Test Data:** flag=context_aware
- **Expected Result:** No outage; off-state behavior as specified
- **Actual Result:**
- **Status:**
- **Postconditions:** Restore flag on
- **Tags/Labels:** Feature Flag, Migration
- **Test Type:** Migration
- **AC Tag(s):** AC-1, AC-2

## PR-IMPACT
- Additional tests from PR gptverse#682 saved at `Innovative Quality Initiatives-AI/pr_test_cases/PR-IO-136500.md`.
