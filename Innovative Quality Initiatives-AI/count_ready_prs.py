#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Set

import requests


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
        print("COUNT=0")
        return

    s = requests.Session()
    s.headers.update({
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {gh_token}",
        "User-Agent": "io-pr-counter/1.0",
    })

    cutoff = datetime.utcnow() - timedelta(days=90)
    page = 1
    count = 0
    latest_url = None
    latest_dt: Optional[datetime] = None
    owner = "celigo"
    repo = "celigo-qa-automation"
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
                print(f"COUNT={count}")
                if latest_url:
                    print(f"LATEST_URL={latest_url}")
                return
            title = (pr.get("title") or "").upper()
            body = (pr.get("body") or "").upper()
            head = (((pr.get("head") or {}).get("ref")) or "").upper()
            matched = any(k in title or k in body or k in head for k in keys)
            if matched:
                count += 1
                if latest_dt is None or (dt and dt > latest_dt):
                    latest_dt = dt
                    latest_url = pr.get("html_url")
        if len(items) < 100:
            break
        page += 1
    print(f"COUNT={count}")
    if latest_url:
        print(f"LATEST_URL={latest_url}")


if __name__ == "__main__":
    main()

