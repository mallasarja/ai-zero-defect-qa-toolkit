### Innovative Quality Initiatives — AI-Assisted QA Automation

- **Presenter**: QA Engineering
- **Date**: Today
- **Repository**: `cursor-api-demo`

### Project Title
- **Innovative Quality Initiatives — AI for Test Generation, Coverage & Readiness**

### Project Objectives
- **Generate comprehensive test suites** (PR, Jira, Zendesk) across 12 categories
- **Identify regression candidates** from Zendesk and Slack E2E signals
- **Normalize tests to IO-style** verbs and best practices
- **Assess automation readiness** and prioritize implementation
- **Track coverage vs Jira stories** and summarize status for stakeholders

### Strategic Goals
- **Reduce escaped bugs** and regressions by targeted regression suites
- **Increase automation coverage** on critical paths (flows, HTTP connectors, payments)
- **Shorten validation cycle time** for PRs and releases
- **Improve test realism** using IO-style steps and realistic data
- **Create reusable utilities** and prompts to standardize generation

### Technologies Used
- **Python** scripts for data processing and generation
- **Markdown** for human-readable reports and slide-style docs
- **CSV** for tabular inputs/outputs where needed
- **Jira API** for story snapshots and AC extraction
- **GitHub API/CSV** for PR discovery and context
- **Slack CSV** for E2E issue normalization and regression candidate selection
- **GitHub for storage/deployment** — outputs committed to repo

### Project Value to QA Team
- **Faster test creation** across PRs, stories, and support tickets
- **Higher-signal regression suites** rooted in real customer incidents & Slack threads
- **Consistent format** and IO-style vocabulary across teams
- **Actionable readiness**: Clear automate vs manual recommendations
- **Better stakeholder visibility** via concise coverage, priority, and readiness summaries

### Data Inputs (Current Workspace)
- `Innovative Quality Initiatives-AI/cleaned_zendesk_issues.csv`
- `Innovative Quality Initiatives-AI/ready_prs_last_90d.csv`
- `Innovative Quality Initiatives-AI/E2E-Issues reported through Slack.csv`
- Jira snapshots (e.g., `jira_inputs/IO-141368_story.md`, `jira_inputs/IO-136500_story.md`)
- PR context from linked development panels

### What Are We Doing in This Project?
- Building an AI-assisted pipeline that:
  - Pulls context from PRs, Jira, Zendesk, and Slack
  - Generates detailed test suites (12 categories) using standardized prompts
  - Normalizes tests into IO-style steps and assertions
  - Evaluates automation readiness and prioritizes by risk
  - Produces roll-up summaries for leadership

### What Tool or Utility Will Be Built?
- **Reusable Test Case Generation Utility**
  - Reads a Jira/PR/Zendesk reference
  - Applies the appropriate prompt template
  - Saves generated suites to the respective folder
  - Optionally runs automation-readiness on the outputs and saves an execution plan

### How This Project Aligns With Celigo’s QA Goals
- **Customer-centric**: Regression candidates surfaced from Zendesk and Slack
- **Platform-realistic**: IO-style verbs and backend reliability patterns
- **Data-driven**: Coverage and readiness metrics to guide investments
- **Continuous**: Re-run on new PRs/stories each sprint

### How It Helps the QA Team (Day-to-Day)
- **Templates & prompts ready-to-use**
- **One-click generation** of comprehensive suites
- **Clear next steps** via action items and readiness assessments
- **Traceability** between Jira/PRs and tests

### Step-by-Step Executions (Team Workflow)
- **Environment**: repo root `/Users/mallasarja/cursor-api-demo`

- **PR discovery & generation**
  - `python3 "Innovative Quality Initiatives-AI/list_ready_prs.py"`
  - `python3 "Innovative Quality Initiatives-AI/generate_test_cases_for_all_prs.py"`
  - Outputs: `Innovative Quality Initiatives-AI/pr_test_cases/PR-<num>_structured_test_cases.md`

- **Combine PR suites (readable report)**
  - `python3 "Innovative Quality Initiatives-AI/combine_pr_test_cases_md.py"`
  - Output: `Innovative Quality Initiatives-AI/pr_test_cases_all.md`

- **Jira story snapshot & suites**
  - `python3 fetch_single_jira_story.py IO-141368`
  - Generate suites using prompts (see Step 4/7)

- **Zendesk regression selection & suites**
  - Identify: `Innovative Quality Initiatives-AI/zd_regression_candidates.md`
  - Generate: `Innovative Quality Initiatives-AI/zd_test_cases/ZD-<id>.md`

- **Slack E2E normalization → candidates → dedup**
  - Outputs: `slack_e2e/normalized.csv`, `slack_e2e/candidates.csv`, `slack_e2e/candidates_dedup.csv`, `slack_e2e/clusters.md`

- **Automation readiness**
  - Run per suite and save under `automation_plan/` (see Step 7)

### Inputs / Data Sources Used
- **Jira**: Story key, summary, description, AC, labels/components, development links
- **GitHub**: PR title/desc, changed files, diff hotspots, linked issues
- **Zendesk**: Filtered tickets meeting regression/escape criteria
- **Slack**: Normalized threads with prod flags, severity hints, Jira keys, flow/job IDs

### Detailed Steps with Valid Prompts (Step 1 → Step 7)

- **Step 1 — PR Test Case Generation**
  - Location: `prompts/pr_testcase_prompt.txt`
```markdown
You are generating 12-category test cases for GitHub PR <PR_URL>.
Include: Functional, Regression, Negative, Manual unit, Integration, API, Performance, Security, Scalability/Reliability/Recovery/Redundancy/Race, E2E, Compatibility, Error handling.
Ensure: Positive/negative/edge cases; realistic data; separate UI vs Backend.
Format each case with fields: Test Case ID, Title/Description, Preconditions, Test Steps, Test Data, Expected Result, Actual Result, Status, Postconditions, Tags/Labels, Test Type.
Use IO verbs where applicable.
```
  - Output folder: `Innovative Quality Initiatives-AI/pr_test_cases/`

- **Step 2 — Zendesk Regression Candidate Identification**
  - Input: `Innovative Quality Initiatives-AI/cleaned_zendesk_issues.csv`
```markdown
Apply filters:
1) Type=BUG (exclude NAN/Feature Request)
2) Regression/Escape=Escape or Yes
3) Test case available?=No or blank
4) Customer issue=True
5) Caused due to release=Yes
6) Resolution comment mentions fix/hotfix/rollback/revert/code change
7) Jira ID valid
Return: Zendesk URL, Jira ID, Summary from Resolution Comment, Reason, Suggested filename.
```
  - Output: `Innovative Quality Initiatives-AI/zd_regression_candidates.md`

- **Step 3 — Zendesk Regression Test Case Generation**
  - Location: `prompts/zd_regression_prompt.txt`
```markdown
Generate Regression, Edge Case, Error Handling, and Functional tests for ZD ticket <ZD_URL>.
Separate UI vs Backend; include realistic data.
Use fields: Test Case ID, Title/Description, Preconditions, Test Steps, Test Data, Expected Result, Actual Result, Status, Postconditions, Tags/Labels, Test Type.
```
  - Output folder: `Innovative Quality Initiatives-AI/zd_test_cases/`

- **Step 4 — Jira Story UI/BE Test Case Generation**
  - Location: `prompts/jira_testcase_prompt.txt`
```markdown
Given Jira story <JIRA_KEY> with ACs and linked PR context, generate 12-category tests.
Use IO-style verbs: Create flow → Configure export/import → Set mappings → Run flow → Check dashboard/logs → Inspect HTTP responses.
Include WCAG 2.1 checks for UI stories.
Format: required fields as above.
```
  - Output folder: `Innovative Quality Initiatives-AI/jira_stories/`

- **Step 5 — Accessibility (WCAG 2.1) Test Generation**
  - Input example: `Innovative Quality Initiatives-AI/sample_ui/LoginForm.jsx`
```markdown
Analyze component for WCAG 2.1 issues: alt-text, keyboard nav, ARIA roles/labels, color contrast, semantic HTML.
Generate test cases with: Test Case ID, Title/Description, Preconditions, Test Steps, Expected Result, Tags/Labels, Test Type.
```
  - Output: `Innovative Quality Initiatives-AI/accessibility/LoginForm_a11y_report_and_tests.md`

- **Step 6 — Performance/Load/Stress/Recovery Scenarios**
  - Input example: API usage patterns (GET /orders 6000 rpm, POST /payment 3000 rpm, PUT /shipment 2500 rpm)
```markdown
Create ramp-up, spike, soak, and recovery tests for given endpoints.
For each: Test Case ID, Load Profile, Preconditions, Test Steps, Expected Result, Tags, Test Type.
```
  - Output: `Innovative Quality Initiatives-AI/api_performance_tests.md`

- **Step 7 — Reusable Test Case Generation Utility + Automation Readiness**
  - Prompts: `prompts/jira_testcase_prompt.txt`, `prompts/pr_testcase_prompt.txt`, `prompts/zd_regression_prompt.txt`, `prompts/automation_readiness_prompt.txt`
```markdown
Given a source (Jira/PR/ZD), apply the corresponding prompt and save tests under:
- Jira → /jira_stories/
- PR → /pr_test_cases/
- Zendesk → /zd_test_cases/
Then evaluate automation readiness using automation_readiness_prompt.txt and save to /automation_plan/<source>-automation-readiness.md.
```

### Team Action Items (With Prompts and Steps)
- **QA/SDET**
  - Run PR/Jira/ZD generation with the provided prompts and verify realism
  - Normalize suites to IO-style; tag regression and customer-impact
  - Execute automation readiness and plan sprint automation
- **Developers**
  - Link PRs to stories and provide change summaries (files/functions, flags)
  - Review PR-impact tests and add missing scenarios
- **Leads/PM**
  - Review stakeholder summaries and prioritize gaps/regressions

### Major Challenges & How We Solved Them
- Shell syntax & Python inline exec issues → moved to dedicated scripts
- Import error (`generate_test_cases_for_pr`) → fixed relative import
- Missing Jira env vars → explicitly sourced `.env`
- Large file token limits → targeted reads/grep instead of full reads
- Missing directories for Slack outputs → ensured `slack_e2e/*` dirs are created
- Bash loop quoting for PR diffs → corrected quoting/expansion

### Quick File Map (Outputs)
- PR suites → `Innovative Quality Initiatives-AI/pr_test_cases/`
- Jira suites → `Innovative Quality Initiatives-AI/jira_stories/`
- Zendesk suites → `Innovative Quality Initiatives-AI/zd_test_cases/`
- A11y → `Innovative Quality Initiatives-AI/accessibility/`
- Performance → `Innovative Quality Initiatives-AI/api_performance_tests.md`
- Coverage/Status → `io_story_test_coverage.csv`, `io_story_test_coverage_summary.md`, `test_priority_summary.md`, `stakeholder_summary.md`
- Automation plan → `Innovative Quality Initiatives-AI/automation_plan/`
- Slack pipeline → `Innovative Quality Initiatives-AI/slack_e2e/`

### Demo Script (5–8 minutes)
- Show `ready_prs_last_90d.csv` → open 1 PR suite in `pr_test_cases/`
- Open `jira_inputs/IO-141368_story.md` → `jira_stories/IO-141368-testcases_v4.md`
- Show Zendesk candidates → open one `zd_test_cases/ZD-*.md`
- Open `api_performance_tests.md` and corresponding automation readiness file
- Show `stakeholder_summary.md` with coverage and priority roll-ups
