# ZD-254165 — Regression Test Cases

- **Test Case ID:** ZD-254165-REG-001
- **Title/Description:** Regression — Prevent recurrence of multipart hotfix issue
- **Preconditions:** Hotfix build deployed; gateway limits configured
- **Test Steps:**
  - Reproduce customer scenario with multipart upload
  - Verify successful upload and no 5xx during peak
- **Test Data:** Customer-like payloads; boundary variations
- **Expected Result:** Stable success; no errors; logs clean
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** ZD, Regression, API
- **Test Type:** Regression

- **Test Case ID:** ZD-254165-EDGE-001
- **Title/Description:** Edge — Large part counts and network jitter
- **Preconditions:** Fault injection for jitter
- **Test Steps:**
  - Upload with many parts; add 200ms jitter
  - Observe retries and completion
- **Test Data:** 500MB payload; jitter=200ms
- **Expected Result:** Multipart completes; retries bounded
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** ZD, Edge, API
- **Test Type:** Integration











