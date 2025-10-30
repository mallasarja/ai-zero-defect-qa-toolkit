#!/usr/bin/env python3
"""
Fetch Jira bugs via REST API and write to public/mcp_jira_bugs.csv
Required env vars (for Jira Cloud):
  - JIRA_BASE_URL  (e.g., https://your-domain.atlassian.net)
  - JIRA_EMAIL
  - JIRA_API_TOKEN
Optional:
  - JIRA_JQL (default: project=IO AND issuetype=Bug AND created >= -90d)
"""
import os
import csv
import requests

PUBLIC_DIR = os.path.join(os.path.dirname(__file__), 'public')
OUT_CSV = os.path.join(PUBLIC_DIR, 'mcp_jira_bugs.csv')


def fetch_all_issues(base_url: str, auth: tuple, jql: str):
    url = f"{base_url}/rest/api/3/search"
    start_at = 0
    max_results = 100
    issues = []
    headers = {"Accept": "application/json"}

    while True:
        params = {
            "jql": jql,
            "startAt": start_at,
            "maxResults": max_results,
            "fields": "summary,created,resolutiondate,status,priority,labels,components,fixVersions"
        }
        resp = requests.get(url, params=params, auth=auth, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("issues", [])
        if not batch:
            break
        issues.extend(batch)
        start_at += len(batch)
        if start_at >= data.get("total", 0):
            break
    return issues


def normalize_issue(issue: dict):
    key = issue.get("key", "")
    f = issue.get("fields", {})
    summary = f.get("summary", "")
    created = f.get("created") or ""
    resolved = f.get("resolutiondate") or ""
    status = (f.get("status") or {}).get("name", "")
    priority = (f.get("priority") or {}).get("name", "")
    # Severity is organization-specific; fall back to priority if no custom field
    severity = priority or ""
    labels = ";".join(f.get("labels") or [])
    components = ";".join([c.get("name", "") for c in (f.get("components") or []) if c])
    return {
        "issueKey": key,
        "summary": summary,
        "created": created,
        "resolved": resolved,
        "status": status,
        "priority": priority,
        "severity": severity,
        "labels": labels,
        "components": components,
        "Bug Detection Phase": "",
    }


def main():
    base_url = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    token = os.getenv("JIRA_API_TOKEN")
    jql = os.getenv("JIRA_JQL", "project=IO AND issuetype=Bug AND created >= -90d ORDER BY created DESC")

    if not (base_url and email and token):
        print("Jira credentials not provided; skipping fetch.")
        return 0

    os.makedirs(PUBLIC_DIR, exist_ok=True)
    issues = fetch_all_issues(base_url, (email, token), jql)
    rows = [normalize_issue(i) for i in issues]

    fieldnames = [
        "issueKey","summary","created","resolved","status","priority","severity","labels","components","Bug Detection Phase"
    ]
    with open(OUT_CSV, "w", newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"Wrote {len(rows)} issues to {OUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


