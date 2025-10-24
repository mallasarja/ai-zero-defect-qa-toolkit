#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import json
from typing import Any, Dict, List
import requests


def get_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        print(f"Missing env: {name}", file=sys.stderr)
        sys.exit(2)
    return v


def fetch_pr(owner: str, repo: str, number: int, token: str) -> Dict[str, Any]:
    s = requests.Session()
    s.headers.update({
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'Authorization': f'Bearer {token}',
        'User-Agent': 'pr-test-generator/1.0',
    })
    pr = s.get(f'https://api.github.com/repos/{owner}/{repo}/pulls/{number}', timeout=60)
    pr.raise_for_status()
    files = s.get(
        f'https://api.github.com/repos/{owner}/{repo}/pulls/{number}/files',
        params={'per_page': 100},
        timeout=60,
    )
    files.raise_for_status()
    data = pr.json()
    data['files'] = files.json() or []
    return data


def infer_layers(files: List[Dict[str, Any]]) -> List[str]:
    paths = [f.get('filename') or '' for f in files]
    paths_l = ' '.join(paths).lower()
    layers: List[str] = []
    if any(x in paths_l for x in ['ui', 'frontend', 'client', 'react', 'component', '.jsx', '.tsx', '.vue']):
        layers.append('UI')
    if True:
        layers.append('Backend')
    return layers


def write_markdown(pr: Dict[str, Any], out_path: str) -> None:
    number = pr.get('number')
    title = pr.get('title') or ''
    body = pr.get('body') or ''
    files = pr.get('files') or []
    layers = infer_layers(files)

    categories = [
        ('FUNC', 'Functional test cases for new or modified logic'),
        ('REG', 'Regression test cases for potentially impacted features'),
        ('NEG', 'Negative test cases for error conditions or invalid inputs'),
        ('MUNIT', 'Manual unit test cases'),
        ('INTEG', 'Integration test cases'),
        ('API', 'API test cases'),
        ('PERF', 'Performance, stress, and load test cases'),
        ('SEC', 'Security test cases'),
        ('SREL', 'Scalability, reliability, downtime recovery, redundancy, and race condition test cases'),
        ('E2E', 'End-to-End test cases'),
        ('COMP', 'Backward and forward compatibility test cases'),
        ('ERR', 'Error handling test cases'),
    ]

    def block(layer: str, code: str, name: str, variant: str, idx: int) -> str:
        tc_id = f"PR{number}-{layer}-{code}-{variant}{idx}"
        lines = []
        lines.append(f"- **Test Case ID:** {tc_id}")
        lines.append(f"- **Title/Description:** {name} — {layer} — {variant}")
        lines.append("- **Preconditions:**")
        lines.append("  - Build deployed; configs valid; feature flags as needed")
        lines.append("- **Test Steps:")
        lines.append("  1. Prepare environment and inputs")
        lines.append("  2. Execute the scenario")
        lines.append("  3. Observe outputs/logs")
        lines.append("- **Test Data:**")
        lines.append("  - Provide realistic records, auth, and payloads as applicable")
        lines.append("- **Expected Result:**")
        if variant == 'Positive':
            lines.append("  - Operation succeeds; outputs correct; no errors in logs")
        elif variant == 'Negative':
            lines.append("  - Clear validation/handling; bounded retries; no crash")
        else:
            lines.append("  - Behavior conforms to policy under extremes; no data loss")
        lines.append("- **Actual Result:** TBD")
        lines.append("- **Status:** Not Executed")
        lines.append("- **Postconditions:** System stable; resources cleaned up")
        lines.append(f"- **Tags/Labels:** [{layer}, {code}, {variant}]")
        lines.append(f"- **Test Type:** {name}")
        return "\n".join(lines)

    md: List[str] = []
    md.append(f"# PR #{number}: {title}")
    md.append("")
    if body:
        md.append("## Description")
        md.append(body)
        md.append("")
    if files:
        md.append("## Changed Files (summary)")
        for f in files:
            md.append(f"- {f.get('filename')} (+{f.get('additions')}/-{f.get('deletions')})")
        md.append("")

    for code, name in categories:
        md.append(f"## {name}")
        for layer in layers:
            md.append(f"### Layer: {layer}")
            md.append(block(layer, code, name, 'Positive', 1))
            md.append("")
            md.append(block(layer, code, name, 'Negative', 1))
            md.append("")
            md.append(block(layer, code, name, 'Edge', 1))
            md.append("")

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md))


def main() -> None:
    token = get_env('GITHUB_TOKEN')
    owner = 'celigo'
    repo = 'celigo-qa-automation'
    number = int(sys.argv[1]) if len(sys.argv) > 1 else 14192
    pr = fetch_pr(owner, repo, number, token)
    out = os.path.join(os.path.dirname(__file__), f'PR-{number}_structured_test_cases.md')
    write_markdown(pr, out)
    print(out)


if __name__ == '__main__':
    main()

