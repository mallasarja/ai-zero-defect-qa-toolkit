# IO-136500 — Backend Test Suite (Context Aware Response Part - 1)

## Functional
- **Test Case ID:** IO-136500-FUNC-001
- **Title/Description:** Generate context-aware answer with page URL and context flags
- **Preconditions:** Service up; env vars: CONTEXT_SERVICE_URL, GPT_KB_URL; feature flag context_aware=true
- **Test Steps:**
  - Call POST /v1/gptverse/knowledge-base/answer with url, context_aware=true, context_value="Already Extracted Context", query
  - Verify 200 OK and markdown response chunked (stream=true)
  - Validate suggestions and links blocks present
- **Test Data:** payload { query:"How do I add a source?", url:"https://app.io/pageA", context_aware:true, context_value:"Already Extracted Context", return_sources:true, max_sources:3, response_format:"markdown", stream:true, thread_id:"thread_abc" }
- **Expected Result:** Structured stream frames; suggestions JSON and links JSON appended; no schema errors
- **Actual Result:**
- **Status:**
- **Postconditions:** N/A
- **Tags/Labels:** API, Functional, Context
- **Test Type:** Functional
- **AC Tag(s):** AC-1, AC-2

- **Test Case ID:** IO-136500-FUNC-002
- **Title/Description:** Fallback when context_value=None uses page URL to infer context
- **Preconditions:** Context resolver online
- **Test Steps:**
  - POST answer with context_value=None
  - Check logs for context-resolution call and resolved scope
- **Test Data:** { context_value:null, url:"https://app.io/flows/123" }
- **Expected Result:** Context inferred; answer aligns to page
- **Actual Result:**
- **Status:**
- **Postconditions:** N/A
- **Tags/Labels:** API, Functional, Context
- **Test Type:** Functional
- **AC Tag(s):** AC-1

## Regression
- **Test Case ID:** IO-136500-REG-001
- **Title/Description:** Ensure streaming format unchanged for consumers
- **Preconditions:** Known consumer expects data: lines
- **Test Steps:**
  - Capture stream; validate prefix data:
