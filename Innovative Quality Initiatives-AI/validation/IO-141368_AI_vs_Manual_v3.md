# Executive Summary
- Verdict: AI stronger
- AI score: 22.82/30 (76.07%), Manual score: 10.0/30 (33.33%)
- Quality Bar — AI: FAIL, Manual: FAIL

## Acceptance Criteria Coverage Matrix
| AC | Manual IDs | AI IDs | Verdict |
|---|---|---|---|
| path to records not mandatory when batchsize > 1 | IO-T49188, IO-T49195, IO-T49196 | IO-141368-FUNC-001, IO-141368-REG-001, IO-141368-NEG-001, IO-141368-INT-001, IO-141368-PERF-001, IO-141368-COMP-001, IO-141368-ERR-001 | Fully |
| override request media type plain text shows number of records per request | IO-T49188, IO-T49189, IO-T49195 | IO-141368-FUNC-001, IO-141368-FUNC-002 | Fully |
| first record contains header checkbox optional default unchecked and visible only when number of records per request > 1 | IO-T49188, IO-T49192, IO-T49193, IO-T49195, IO-T49196 | IO-141368-FUNC-001, IO-141368-FUNC-003 | Fully |
| help text includes be field import.http.response.hasHeader | IO-T49188, IO-T49189, IO-T49194, IO-T49195 | - | Partial |

## Mapping Table (Manual ↔ AI)
| Manual ID | Manual Title | AI ID | AI Title | Similarity | Category |
|---|---|---|---|---:|---|
| IO-T49188 | ** Test to validate Path to records in HTTP response body field is not mandatory when Number of records per HTTP request > 1. | IO-141368-FUNC-001 | ** Path to records is not mandatory when Number of records per HTTP request > 1 | 0.79 | Close |
| - **Title/Description:** |  | IO-141368-FUNC-001 | ** Path to records is not mandatory when Number of records per HTTP request > 1 | 0.00 | Unmapped |
| IO-T49189 | ** Test to validate When "Override request media type" is set to plain text in the import, the "Number of records per HTTP request" should show and the value should be retained when saved and closed | IO-141368-FUNC-002 | ** Show “Number of records per HTTP request” when Override request media type=plain/text | 0.73 | Partial |
| IO-T49190 | ** Test to validate "First Record contains header" is added on the imports | IO-141368-FUNC-003 | ** “First Record contains header” checkbox present and optional | 0.36 | Unmapped |
| IO-T49191 | ** Test to validate the help text for "First Record contains header" | IO-141368-FUNC-003 | ** “First Record contains header” checkbox present and optional | 0.36 | Unmapped |
| IO-T49192 | ** Test to validate "First Record contains header" checkbox is unchecked by default | IO-141368-FUNC-003 | ** “First Record contains header” checkbox present and optional | 0.42 | Unmapped |
| IO-T49193 | ** Test to validate "First Record contains header" checkbox is optional | IO-141368-FUNC-003 | ** “First Record contains header” checkbox present and optional | 0.67 | Partial |
| IO-T49194 | ** Test to validate the path on helptext fields "BE field: import.http.response.hasHeader" | IO-141368-INT-001 | ** Path-less import when batchSize>1 with downstream mapping | 0.28 | Unmapped |
| IO-T49195 | ** Test to validate Path to records in HTTP response body field is not visible when the Number of records per HTTP request is less than < or equal = to 1 | IO-141368-FUNC-001 | ** Path to records is not mandatory when Number of records per HTTP request > 1 | 0.59 | Unmapped |
| IO-T49196 | ** Test to validate First record contains headers field is visible only when the Number of records is >1 | IO-141368-FUNC-003 | ** “First Record contains header” checkbox present and optional | 0.34 | Unmapped |

## Gaps in Manual (Manual lacks but AI/AC demands)
- AI IO-141368-REG-001: ** Backward-compatibility when batchSize ≤ 1 hides Path to records — Add manual coverage
- AI IO-141368-REG-002: ** Persist batchSize after save/close when mediaType=plain/text — Add manual coverage
- AI IO-141368-NEG-001: ** Validation does not block when path empty and batchSize>1 — Add manual coverage
- AI IO-141368-MUNIT-001: ** Unit—UI element visibility toggles per batchSize — Add manual coverage
- AI IO-141368-INT-001: ** Path-less import when batchSize>1 with downstream mapping — Add manual coverage
- AI IO-141368-API-001: ** Verify import configuration via API reflects UI rules — Add manual coverage
- AI IO-141368-PERF-001: ** Performance—import throughput with batchSize>1 — Add manual coverage
- AI IO-141368-SEC-001: ** No unintended elevation via hidden fields — Add manual coverage
- AI IO-141368-SREL-001: ** Recovery—restart during config save — Add manual coverage
- AI IO-141368-E2E-001: ** E2E—Create flow, Configure import, Run flow, Verify results — Add manual coverage

## Gaps in AI (AI lacks but Manual/AC demands)
- Manual - **Title/Description:**: 
- **Title/Description:** 
- **Preconditions:** Create flow; Configure import (HTTP); Navigate to Non-standard API response patterns
- **Test Steps:
  - Set relevant batchSize/media type as per case
  - Run flow; Check dashboard run status/logs
  - Inspect HTTP response & error payloads
- **Test Data:** HTTP import; JSON/Plain text per case; batchSize per rule
- **Expected Result:** UI reflects rule; values persist; no validation error
- **Tags/Labels:** UI, Regression
- **Test Type:** Functional
- Manual IO-T49190: ** Test to validate "First Record contains header" is added on the imports
- **Title/Description:** ** Test to validate "First Record contains header" is added on the imports
- **Preconditions:** Create flow; Configure import (HTTP); Navigate to Non-standard API response patterns
- **Test Steps:
  - Set relevant batchSize/media type as per case
  - Run flow; Check dashboard run status/logs
  - Inspect HTTP response & error payloads
- **Test Data:** HTTP import; JSON/Plain text per case; batchSize per rule
- **Expected Result:** UI reflects rule; values persist; no validation error
- **Tags/Labels:** UI, Regression
- **Test Type:** Functional
- Manual IO-T49191: ** Test to validate the help text for "First Record contains header"
- **Title/Description:** ** Test to validate the help text for "First Record contains header"
- **Preconditions:** Create flow; Configure import (HTTP); Navigate to Non-standard API response patterns
- **Test Steps:
  - Set relevant batchSize/media type as per case
  - Run flow; Check dashboard run status/logs
  - Inspect HTTP response & error payloads
- **Test Data:** HTTP import; JSON/Plain text per case; batchSize per rule
- **Expected Result:** UI reflects rule; values persist; no validation error
- **Tags/Labels:** UI, Regression
- **Test Type:** Functional
- Manual IO-T49192: ** Test to validate "First Record contains header" checkbox is unchecked by default
- **Title/Description:** ** Test to validate "First Record contains header" checkbox is unchecked by default
- **Preconditions:** Create flow; Configure import (HTTP); Navigate to Non-standard API response patterns
- **Test Steps:
  - Set relevant batchSize/media type as per case
  - Run flow; Check dashboard run status/logs
  - Inspect HTTP response & error payloads
- **Test Data:** HTTP import; JSON/Plain text per case; batchSize per rule
- **Expected Result:** UI reflects rule; values persist; no validation error
- **Tags/Labels:** UI, Regression
- **Test Type:** Functional
- Manual IO-T49194: ** Test to validate the path on helptext fields "BE field: import.http.response.hasHeader"
- **Title/Description:** ** Test to validate the path on helptext fields "BE field: import.http.response.hasHeader"
- **Preconditions:** Create flow; Configure import (HTTP); Navigate to Non-standard API response patterns
- **Test Steps:
  - Set relevant batchSize/media type as per case
  - Run flow; Check dashboard run status/logs
  - Inspect HTTP response & error payloads
- **Test Data:** HTTP import; JSON/Plain text per case; batchSize per rule
- **Expected Result:** UI reflects rule; values persist; no validation error
- **Tags/Labels:** UI, Regression
- **Test Type:** Functional
- Manual IO-T49195: ** Test to validate Path to records in HTTP response body field is not visible when the Number of records per HTTP request is less than < or equal = to 1
- **Title/Description:** ** Test to validate Path to records in HTTP response body field is not visible when the Number of records per HTTP request is less than < or equal = to 1
- **Preconditions:** Create flow; Configure import (HTTP); Navigate to Non-standard API response patterns
- **Test Steps:
  - Set relevant batchSize/media type as per case
  - Run flow; Check dashboard run status/logs
  - Inspect HTTP response & error payloads
- **Test Data:** HTTP import; JSON/Plain text per case; batchSize per rule
- **Expected Result:** UI reflects rule; values persist; no validation error
- **Tags/Labels:** UI, Regression
- **Test Type:** Functional
- Manual IO-T49196: ** Test to validate First record contains headers field is visible only when the Number of records is >1
- **Title/Description:** ** Test to validate First record contains headers field is visible only when the Number of records is >1
- **Preconditions:** Create flow; Configure import (HTTP); Navigate to Non-standard API response patterns
- **Test Steps:
  - Set relevant batchSize/media type as per case
  - Run flow; Check dashboard run status/logs
  - Inspect HTTP response & error payloads
- **Test Data:** HTTP import; JSON/Plain text per case; batchSize per rule
- **Expected Result:** UI reflects rule; values persist; no validation error
- **Tags/Labels:** UI, Regression
- **Test Type:** Functional

## Parity checks (UI vs API/config)
- Add tests to ensure UI checkbox visibility aligns with import.http.response.hasHeader and batchSize rules.

## A11y Coverage
- AI a11y cases: 1; Manual a11y cases: 0. Ensure keyboard/focus/aria/contrast present for each UI change.

## Quality Checks
- IO realism: AI 61.54%, Manual 0.0%
- Data realism: AI 75.0%, Manual 0.0%
- Category counts (AI): Functional:4, Regression:2, Negative:0, Manual unit:1, Integration:1, API:1, Performance:1, Security:1, Reliability:0, End-to-End:1, Compatibility:1, Error:1, Accessibility:1
- Category counts (Manual): Functional:10, Regression:0, Negative:0, Manual unit:0, Integration:0, API:0, Performance:0, Security:0, Reliability:0, End-to-End:0, Compatibility:0, Error:0, Accessibility:0

## Top-10 Risk-Prioritized Adds
1. Help text path correctness (import.http.response.hasHeader)
2. Visibility of checkbox only when batchSize>1
3. Persistence of batchSize under plain/text override
4. Negative save with invalid JSON/missing fields
5. API parity for config flags
6. A11y focus order and role=alert/status announcements
7. Regression for batchSize<=1 hiding path
8. RBAC preventing readonly edits
9. Recovery on restart during config save
10. Performance throughput with batchSize>1

## Refined Prompt
Generate IO-style UI test cases for IO-141368 with explicit IO verbs (Create flow, Configure import/export, Set mappings, Run flow, Check dashboard status/logs, Inspect HTTP response/error payloads).
Map each test to an AC tag (AC-1/AC-2/AC-3/AC-4).
Cover: path-not-mandatory when batchSize>1; plain/text override shows & persists batchSize; 'First Record contains header' checkbox: present, default unchecked, optional, help text correct (BE field: import.http.response.hasHeader), visible only when batchSize>1.
Add suites: Integration, API parity, Performance (batchSize>1), Security (RBAC), Recovery (save restart), E2E, Compatibility (batchSize<=1), Error handling, and a11y (keyboard, focus, roles/aria, contrast).
Use realistic Test Data. Include negative & edge for each UI rule.

---
Update Note
- Normalized IO-style suite saved at `Innovative Quality Initiatives-AI/jira_stories/IO-141368-testcases_v4.md`. Use this for re-evaluation.