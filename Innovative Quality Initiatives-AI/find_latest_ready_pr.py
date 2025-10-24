#!/usr/bin/env python3
"""
Find the most recent PR (created in last 90 days) in celigo/celigo-qa-automation
that references an IO Jira issue whose status is in the provided QA statuses.

Env (from .env in this folder):
  - JIRA_BASE_URL
  - JIRA_EMAIL
  - JIRA_API_TOKEN
  - GITHUB_TOKEN

Output:
  - Writes details to Innovative Quality Initiatives-AI/latest_ready_for_qa_pr.txt
  - Prints URL to stdout
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import requests

THIS_DIR = os.path.dirname(__file__)
OUTFILE = os.path.join(THIS_DIR, "latest_ready_for_qa_pr.txt")

GITHUB_OWNER = "celigo"
GITHUB_REPO = "celigo-qa-automation"

# Jira statuses to consider (epic or story)
QA_STATUSES = [
    "QA Ready",
    "QA validation",
    "Open",
    "In Progress",
    "Ready for development",
    "Epic breakdown",
    "Epic testing",
]


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print(f"Missing env: {name}", file=sys.stderr)
        sys.exit(2)
    return value


def fetch_jira_issue_keys(base_url: str, email: str, token: str) -> Set[str]:
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
        params = {
            "jql": jql,
            "startAt": start_at,
            "maxResults": page_size,
            "fields": "key",
        }
        resp = requests.get(url, headers=headers, params=params, auth=auth, timeout=60)
        if resp.status_code in (429, 502, 503, 504):
            time.sleep(int(resp.headers.get("Retry-After", "5")))
            continue
        resp.raise_for_status()
        data = resp.json()
        issues = data.get("issues", [])
        for issue in issues:
            k = (issue.get("key") or "").strip().upper()
            if k:
                keys.add(k)
        if not issues:
            break
        start_at += len(issues)
        total = int(data.get("total", 0))
        if start_at >= total:
            break
    return keys


def github_session(token: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {token}",
        "User-Agent": "io-pr-finder/1.0",
    })
    return s


def iter_recent_prs(s: requests.Session, owner: str, repo: str, days_back: int = 90) -> Iterable[Dict[str, Any]]:
    cutoff = datetime.utcnow() - timedelta(days=days_back)
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    params: Dict[str, Any] = {"state": "all", "per_page": 100, "page": 1, "sort": "created", "direction": "desc"}
    while True:
        resp = s.get(url, params=params, timeout=60)
        resp.raise_for_status()
        items = resp.json() or []
        if not items:
            break
        for pr in items:
            created_at = pr.get("created_at") or ""
            try:
                created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except Exception:
                created_dt = None
            if created_dt and created_dt < cutoff.replace(tzinfo=created_dt.tzinfo):
                return
            yield pr
        if len(items) < 100:
            break
        params["page"] = int(params.get("page", 1)) + 1


def find_latest_matching_pr(keys: Set[str], s: requests.Session) -> Optional[Dict[str, Any]]:
    if not keys:
        return None
    keys_upper = {k.upper() for k in keys}
    latest: Optional[Tuple[datetime, Dict[str, Any], str]] = None
    for pr in iter_recent_prs(s, GITHUB_OWNER, GITHUB_REPO, days_back=90):
        title = (pr.get("title") or "").upper()
        body = (pr.get("body") or "").upper()
        head_ref = (((pr.get("head") or {}).get("ref")) or "").upper()
        created_at = pr.get("created_at") or ""
        try:
            created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except Exception:
            created_dt = datetime.utcnow()
        matched_key = None
        for key in keys_upper:
            if key in title or key in body or key in head_ref:
                matched_key = key
                break
        if matched_key:
            if latest is None or created_dt > latest[0]:
                latest = (created_dt, pr, matched_key)
    return latest[1] if latest else None


def write_output(pr: Dict[str, Any]) -> None:
    url = pr.get("html_url") or pr.get("url") or ""
    title = pr.get("title") or ""
    number = pr.get("number") or ""
    created = pr.get("created_at") or ""
    with open(OUTFILE, "w", encoding="utf-8") as f:
        f.write(f"PR_NUMBER: {number}\n")
        f.write(f"PR_TITLE: {title}\n")
        f.write(f"PR_CREATED_AT: {created}\n")
        f.write(f"PR_URL: {url}\n")
    print(url)


def main() -> None:
    jira_base = get_env("JIRA_BASE_URL")
    jira_email = get_env("JIRA_EMAIL")
    jira_token = get_env("JIRA_API_TOKEN")
    gh_token = get_env("GITHUB_TOKEN")

    keys = fetch_jira_issue_keys(jira_base, jira_email, jira_token)
    if not keys:
        print("No IO Jira issues found in target statuses.")
        sys.exit(0)

    session = github_session(gh_token)
    pr = find_latest_matching_pr(keys, session)
    if not pr:
        print("No matching PR found in last 90 days.")
        sys.exit(0)

    write_output(pr)


if __name__ == "__main__":
    main()

