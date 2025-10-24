#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Set

import requests

OUTFILE = os.path.join(os.path.dirname(__file__), "ready_prs_last_90d.csv")


def get_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        print(f"Missing env: {name}", file=sys.stderr)
        sys.exit(2)
    return v


def fetch_jira_keys(base_url: str, email: str, token: str) -> Set[str]:
    jql = (
        'project = IO AND issuetype in (Story, Epic) AND '
        'status in ("QA Ready", "QA validation", "Open", "In Progress", "Ready for development", "Epic breakdown", "Epic testing") '
        'ORDER BY updated DESC'
    )
    url = base_url.rstrip("/") + "/rest/api/3/search"
    auth = (email, token)
    headers = {"Accept": "application/json"}
    start_at = 0
    page_size = 100
    keys: Set[str] = set()
    while True:
        params = {"jql": jql, "startAt": start_at, "maxResults": page_size, "fields": "key"}
        resp = requests.get(url, headers=headers, params=params, auth=auth, timeout=60)
        if resp.status_code in (429, 502, 503, 504):
            time.sleep(int(resp.headers.get("Retry-After", "5")))
            continue
        resp.raise_for_status()
        data = resp.json()
        issues = data.get("issues", [])
        for it in issues:
            k = (it.get("key") or "").strip().upper()
            if k:
                keys.add(k)
        if not issues:
            break
        start_at += len(issues)
        total = int(data.get("total", 0))
        if start_at >= total:
            break
    return keys


def main() -> None:
    jira_base = get_env("JIRA_BASE_URL")
    jira_email = get_env("JIRA_EMAIL")
    jira_token = get_env("JIRA_API_TOKEN")
    gh_token = get_env("GITHUB_TOKEN")

    keys = fetch_jira_keys(jira_base, jira_email, jira_token)
    if not keys:
        print("No matching Jira issues.")
        return

    s = requests.Session()
    s.headers.update({
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {gh_token}",
        "User-Agent": "io-pr-lister/1.0",
    })

    cutoff = datetime.utcnow() - timedelta(days=90)
    owner = "celigo"
    repo = "celigo-qa-automation"

    rows: List[List[str]] = []
    page = 1
    while True:
        resp = s.get(
            f"https://api.github.com/repos/{owner}/{repo}/pulls",
            params={"state": "all", "per_page": 100, "page": page, "sort": "created", "direction": "desc"},
            timeout=60,
        )
        resp.raise_for_status()
        items = resp.json() or []
        if not items:
            break
        for pr in items:
            created_at = pr.get("created_at") or ""
            try:
                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except Exception:
                dt = None
            if dt and dt < cutoff.replace(tzinfo=dt.tzinfo):
                # stop scan once older than cutoff
                items = []
                break
            title = pr.get("title") or ""
            body = pr.get("body") or ""
            head = ((pr.get("head") or {}).get("ref") or "")
            title_u = title.upper(); body_u = body.upper(); head_u = head.upper()
            matched_key = next((k for k in keys if k in title_u or k in body_u or k in head_u), None)
            if matched_key:
                rows.append([
                    str(pr.get("number") or ""),
                    created_at,
                    pr.get("html_url") or "",
                    matched_key,
                    title.replace("\n"," ").strip(),
                ])
        if len(items) < 100:
            break
        page += 1

    # Write CSV
    with open(OUTFILE, "w", encoding="utf-8") as f:
        f.write("pr_number,created_at,url,matched_issue_key,title\n")
        for r in rows:
            f.write(",".join('"'+c.replace('"','""')+'"' for c in r) + "\n")

    print(f"Wrote {len(rows)} rows to {OUTFILE}")


if __name__ == "__main__":
    main()

