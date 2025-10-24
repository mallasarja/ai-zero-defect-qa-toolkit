## Zero‑Defect Dashboard Runbook

### Overview
This runbook documents the end‑to‑end setup of the Zero‑Defect Dashboard: data ingestion from Jira and GitHub, enrichment and KPI generation, and the React dashboard UI with analytics, quality KPIs, and customer impact.

### Scope: Last 2 Years
- Jira bugs: filtered with `created >= -104w` and `status NOT IN (Rejected, Closed)`.
- GitHub PRs: fixed window `[2023-08-01T00:00:00Z, 2025-08-01T00:00:00Z)`.
- All metrics, joins, and dashboards reflect this 2‑year scope.

### Repository layout (key paths)
- `fetch_mcp_bugs.py`: Jira bugs fetcher → `zero-defect-dashboard/public/mcp_jira_bugs.csv`
- `fetch_github_prs_last_2y.py`: GitHub PR matcher for last 2 years → `zero-defect-dashboard/public/github_prs.csv`
- `join_bugs_with_prs.py`: join bugs with PRs, mark escaped → `zero-defect-dashboard/public/bug_with_pr_link.csv`
- KPI generators:
  - `zero-defect-dashboard/generate_kpis_from_join.py`
    - Outputs: `bug_metrics_dashboard.json`, `bug_severity_distribution.csv`, `bug_priority_distribution.csv`, `bug_trend_releasewise.csv`
  - `zero-defect-dashboard/generate_ai_testing_impact.py`
    - Outputs: `ai_testing_impact.json`
  - `zero-defect-dashboard/generate_automation_coverage.py`
    - Outputs: `automation_coverage.json`, `escaped_without_ai_tests.csv`
  - `zero-defect-dashboard/generate_customer_impact.py`
    - Outputs: `customer_impact.json`
- Dashboard UI (React):
  - `zero-defect-dashboard/dashboard_ui.jsx`
  - Public data folder: `zero-defect-dashboard/public/`

### Prerequisites
- Python 3.9+
- Node.js 18+
- A virtualenv for Python (optional)
- `.env` in repo root with:
  - `JIRA_EMAIL`, `JIRA_TOKEN`
  - `GITHUB_TOKEN`

Example `.env`:
```ini
JIRA_EMAIL=you@company.com
JIRA_TOKEN=your_jira_api_token
GITHUB_TOKEN=your_github_token
```

### Python environment setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U requests python-dotenv urllib3
```

### Node dependencies
```bash
npm install
```

## Step‑by‑step implementation

### 1) Fetch Jira bugs (MCP)
- Script: `fetch_mcp_bugs.py`
- JQL applied:
  - Initially: last 3 years scan
  - Updated per requirement: `project = IO AND issuetype = Bug AND created >= -104w AND status NOT IN (Rejected, Closed)`
- Fields fetched: `summary, status, created, resolutiondate, priority, labels, components`, plus custom fields if present:
  - Severity
  - Bug Detection Phase (to mark escaped defects)
- Output: `zero-defect-dashboard/public/mcp_jira_bugs.csv`

Run:
```bash
python3 fetch_mcp_bugs.py
```

### 2) Fetch GitHub PRs for last 2 years and match to bugs
- Script: `fetch_github_prs_last_2y.py`
- Repo: `celigo/celigo-qa-automation`
- Window: `[2023-08-01T00:00:00Z, 2025-08-01T00:00:00Z)`
- Matching: scan PR title/body and (optionally) commit messages for `IO-xxxxx`; intersects with keys from `mcp_jira_bugs.csv`
- Rate limiting: honors `X-RateLimit-Reset`; exponential backoff
- Output: `zero-defect-dashboard/public/github_prs.csv` with columns: `pr_number,title,body,merged_at,matched_issue_key`

Run (unbuffered logging, commit scan off for speed):
```bash
PYTHONUNBUFFERED=1 GITHUB_INCLUDE_COMMITS=0 \
  .venv/bin/python -u fetch_github_prs_last_2y.py > zero-defect-dashboard/public/github_prs_fetch.log 2>&1 &
```

Notes:
- If too slow, set `GITHUB_INCLUDE_COMMITS=0` to skip commit scans.
- Use `pkill -f fetch_github_prs_last_2y.py` to stop.

### 3) Join bugs and PRs; mark escaped
- Script: `join_bugs_with_prs.py`
- Reads: `mcp_jira_bugs.csv`, `github_prs.csv`
- Adds:
  - `linked_pr_number` (consolidated PR numbers)
  - `is_escaped_defect` from `Bug Detection Phase` = `Production/Escaped (Customer|Internal)`
- Output: `zero-defect-dashboard/public/bug_with_pr_link.csv`

Run:
```bash
python3 join_bugs_with_prs.py
```

### 4) Generate KPI datasets (metrics, distributions, trends)
- Script: `zero-defect-dashboard/generate_kpis_from_join.py`
- Outputs:
  - `bug_metrics_dashboard.json` with `total_bugs, escaped_bugs, pr_linked_bugs, avg_mttr`
  - `bug_severity_distribution.csv` grouped by `severity`
  - `bug_priority_distribution.csv` grouped by `priority`
  - `bug_trend_releasewise.csv` grouped by release (fallback to created month if release is unavailable)

Run:
```bash
python3 zero-defect-dashboard/generate_kpis_from_join.py
```

### 5) AI testing impact
- Script: `zero-defect-dashboard/generate_ai_testing_impact.py`
- Reads both:
  - `public/zephyr_tests.csv` (labels column)
  - `public/mcp_jira_bugs.csv` (labels column)
- Counts `AI_Generated` by created month, aggregates total
- Output: `public/ai_testing_impact.json`

Run:
```bash
python3 zero-defect-dashboard/generate_ai_testing_impact.py
```

### 6) Automation coverage and escaped bugs without automated tests
- Script: `zero-defect-dashboard/generate_automation_coverage.py`
- Automated if either:
  - `Automation Status` in {API Automated, Automated, Automated via unit test, To be Automated API, To be Automated UI, Playwright Automated}
  - OR `automated` column is Yes/True
- Outputs:
  - `public/automation_coverage.json` with overall percent and per‑module table
  - `public/escaped_without_ai_tests.csv` listing escaped defects with no automated tests

Run:
```bash
python3 zero-defect-dashboard/generate_automation_coverage.py
```

### 7) Customer impact (Zendesk) and bug linkage
- Script: `zero-defect-dashboard/generate_customer_impact.py`
- Reads:
  - `zendesk_issues.csv` (root folder)
  - `public/bug_with_pr_link.csv`
- Extracts `IO-xxxxx` from `Jira Id` in Zendesk and links to bug priority/severity
- Outputs `public/customer_impact.json` with:
  - totals: `total_zendesk_tickets, total_linked_tickets, total_escaped_bugs`
  - `monthly_trend`: tickets vs escaped vs linked per month
  - `linked_breakdown`: by priority and severity

Run:
```bash
python3 zero-defect-dashboard/generate_customer_impact.py
```

## Dashboard UI
- Component: `zero-defect-dashboard/dashboard_ui.jsx`
- Data loaded at runtime from `zero-defect-dashboard/public/`:
  - `bug_with_pr_link.csv`
  - `bug_metrics_dashboard.json`
  - `bug_severity_distribution.csv`
  - `bug_priority_distribution.csv`
  - `bug_trend_releasewise.csv`
  - `automation_coverage.json`
  - `ai_testing_impact.json`
  - `escaped_without_ai_tests.csv`
  - `customer_impact.json`

### Key UI features
- Summary cards: Total, Escaped, PR‑linked, Avg MTTR
- Analytics:
  - Line chart: Bugs by Release (from `bug_trend_releasewise.csv`)
  - Pie charts: by Severity and by Priority
- Zero‑Defect Monitor: Escaped P1/P2 (by priority), latest first
- Filters: Severity, Priority, Escaped
- Bug table: shows only valid bugs (linked PRs or escaped); invalid count (Duplicate/Rejected)
- Customer Impact: totals, monthly linked vs escaped, and breakdown lists
- Release‑wise trend and “Escaped without automated tests” section above Bug Details

### Run the dashboard
Dev server (recommended):
```bash
npm run dashboard
# opens http://localhost:3000
```

Static server (only for static HTML; not recommended for React bundle):
```bash
cd zero-defect-dashboard
python3 -m http.server 8080
# then open http://localhost:8080 — note: this won’t load the React bundle
```

## Prompts log (condensed)
- “Create a Python script called fetch_mcp_bugs.py that: Connects to Jira Cloud using credentials from the .env file (JIRA_EMAIL and JIRA_TOKEN). Runs JQL: project = IO AND issuetype = Bug AND created >= -104w AND status NOT IN (Rejected, Closed). Fetch fields … Save and update CSV zero-defect-dashboard/public/mcp_jira_bugs.csv.”
- “Create a script fetch_github_prs_last_2y.py that: Loads all Jira issue keys… connects to celigo/celigo-qa-automation… Fetches PRs merged_at >= \"2023-08-01T00:00:00Z\" AND < \"2025-08-01T00:00:00Z\"… Scans title/body/commit messages… Save to zero-defect-dashboard/public/github_prs.csv… Respect rate limits.”
- “Kill the background Python process.” / “tail -n 50 -f …github_prs_fetch.log.” / “Run unbuffered with PYTHONUNBUFFERED=1.” / “Disable commit scans (titles/body only).”
- “Create join_bugs_with_prs.py to: Read mcp_jira_bugs.csv and github_prs.csv; Match on issueKey; Add column 'linked_pr_number'; Add 'is_escaped_defect' from Bug Detection Phase; Save bug_with_pr_link.csv.”
- “From bug_with_pr_link.csv: Generate bug_metrics_dashboard.json (total_bugs, escaped_bugs, pr_linked_bugs, avg_mttr); Create bug_severity_distribution.csv, bug_priority_distribution.csv; Create bug_trend_releasewise.csv (grouped by release if available).”
- “From zephyr_tests.csv and/or mcp_jira_bugs.csv: Count AI_Generated by created month; Save ai_testing_impact.json.”
- “Use zephyr_tests.csv to mark automated statuses … Output automation_coverage.json and escaped_without_ai_tests.csv.”
- “Update dashboard_ui.jsx to: Add priority dropdown; Add Escaped P1/P2; Load release trends and priority pie; Load coverage/AI; Show escaped_without_ai_tests; Only valid bugs; Count invalid bugs.”
- “Enhance with Zendesk: Link tickets to bugs; Add customer_impact.json and show trend and breakdowns.”
- “Fix runtime error getUniquePriorities is not defined.” / “Harden null checks for JSON fields.”
- “Switch chart to release‑wise; move Release Trend and Escaped Without Tests above Bug Details.”

## Detailed prompts and responses (key excerpts)

1) Fetch Jira bugs
```text
Create a Python script called fetch_mcp_bugs.py that:
1. Connects to Jira Cloud using credentials from the .env file (JIRA_EMAIL and JIRA_TOKEN).
2. Runs the following JQL query:
   project = IO AND issuetype = Bug AND created >= -104w AND status NOT IN (Rejected, Closed)
3. For each bug, fetch these fields: issueKey, summary, created, resolved, status, priority, severity, labels, components, Bug Detection Phase
4. Save CSV zero-defect-dashboard/public/mcp_jira_bugs.csv
```

2) Fetch GitHub PRs (2 years)
```text
Create a script fetch_github_prs_last_2y.py that:
- Loads all Jira issue keys from public/mcp_jira_bugs.csv
- Connects to GitHub repo 'celigo/celigo-qa-automation' using GITHUB_TOKEN from .env
- Fetches PRs with merged_at >= "2023-08-01T00:00:00Z" AND < "2025-08-01T00:00:00Z"
- Paginates using Link headers
- Scans PR title/body/commit messages; If any contain IO-xxxxx → mark as match
- Save to zero-defect-dashboard/public/github_prs.csv
- Respect rate limits using X-RateLimit-Reset header
```

3) Join and enrich
```text
Create join_bugs_with_prs.py to:
- Read mcp_jira_bugs.csv and github_prs.csv
- Match on issueKey
- Add column 'linked_pr_number' to bugs if matched
- Add 'is_escaped_defect' using 'Bug Detection Phase'
- Save to zero-defect-dashboard/public/bug_with_pr_link.csv
```

4) KPI generation
```text
From bug_with_pr_link.csv:
- Generate bug_metrics_dashboard.json (total_bugs, escaped_bugs, pr_linked_bugs, avg_mttr)
- Create bug_severity_distribution.csv; bug_priority_distribution.csv
- Create bug_trend_releasewise.csv (grouped by release version if available)
```

5) AI testing
```text
From zephyr_tests.csv and/or mcp_jira_bugs.csv:
- Count test cases labeled 'AI_Generated'
- Group by created month
- Save total count and monthly trend in ai_testing_impact.json
```

6) Automation coverage
```text
Use zephyr_tests.csv to:
- Treat the following Automation_Status values as automated: 'API Automated', 'Automated', 'Automated via unit test', 'To be Automated API', 'To be Automated UI', 'Playwright Automated'
- Everything else as manual
- For each module: Count total tests; Count automated; Compute coverage %
- Output automation_coverage.json
- Cross-reference mcp_jira_bugs.csv to identify escaped bugs without matching automated test
- Output escaped_without_ai_tests.csv
```

7) UI updates and release trend
```text
Update dashboard_ui.jsx to:
- Add priority dropdown (separate from severity)
- Add Escaped P1/P2 monitor panel using is_escaped_defect + priority
- Load bug_trend_releasewise.csv for trends (fallback to month if no release)
- Add pie chart for bug_priority_distribution.csv
- Load automation_coverage.json and ai_testing_impact.json
- Show table for escaped_without_ai_tests.csv
- Table should show all valid bugs (with linked PRs or escaped defect)
- Also show count of invalid bugs (status = Duplicate, Rejected, etc.)
```

8) Customer impact
```text
yes for more better we can use zendesk ticket linked to bugs … expand customer_impact.json with severity/priority slices or ticket CSAT once available.
```

## Challenges and resolutions
- Missing Python modules (`requests`, `python-dotenv`): installed into venv.
- Rate limits and slow PR scans: added backoff; disabled commit scans for speed with `GITHUB_INCLUDE_COMMITS=0`.
- Buffered logs hiding progress: ran Python unbuffered (`PYTHONUNBUFFERED=1`, `-u`).
- CSV header/schema drift: normalized columns and added null/undefined guards in React.
- UI runtime error: undefined `getUniquePriorities()` — implemented helper and added guards.
- Static hosting showed blank page: used webpack dev server to inject React bundle and serve public data.
- Release grouping absent in data: generator falls back to month grouping to keep chart populated.

## Maintenance and updates
- Refresh data:
```bash
python3 fetch_mcp_bugs.py
python3 fetch_github_prs_last_2y.py   # optionally with GITHUB_INCLUDE_COMMITS=0
python3 join_bugs_with_prs.py
python3 zero-defect-dashboard/generate_kpis_from_join.py
python3 zero-defect-dashboard/generate_ai_testing_impact.py
python3 zero-defect-dashboard/generate_automation_coverage.py
python3 zero-defect-dashboard/generate_customer_impact.py
```
- Rebuild UI:
```bash
npm run dashboard
```

### Data contracts (inputs → outputs)
- Inputs: `mcp_jira_bugs.csv`, `github_prs.csv`, `zephyr_tests.csv`, `zendesk_issues.csv`
- Outputs consumed by UI under `zero-defect-dashboard/public/`:
  - `bug_with_pr_link.csv`, `bug_metrics_dashboard.json`, `bug_severity_distribution.csv`, `bug_priority_distribution.csv`, `bug_trend_releasewise.csv`, `automation_coverage.json`, `ai_testing_impact.json`, `escaped_without_ai_tests.csv`, `customer_impact.json`

### Tips
- Keep `.env` tokens valid.
- For large PR scans, prefer commit scans OFF first; re‑run with commit scans ON if needed for higher link coverage.
- Ensure all CSV/JSON are present under `zero-defect-dashboard/public/` before starting the dev server.