#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import csv
from typing import Dict, List, Tuple, Optional

BASE_DIR = os.path.dirname(__file__)
MD_INPUT = os.path.join(BASE_DIR, 'zd_regression_candidates.md')
CSV_SRC = os.path.join(BASE_DIR, 'cleaned_zendesk_issues.csv')
OUT_DIR = os.path.join(BASE_DIR, 'zd_test_cases')


TicketInfo = Tuple[str, str, str, str]  # (ticket_url, jira_id, summary, suggested_filename)


def read_candidates_md(path: str) -> List[TicketInfo]:
    tickets: List[TicketInfo] = []
    if not os.path.exists(path):
        return tickets
    ticket_url = jira_id = summary = filename = ''
    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if line.startswith('- Zendesk Ticket:') or line.startswith('- Zendesk Ticket URL:'):
                ticket_url = line.split(':', 1)[1].strip()
            elif line.startswith('- Jira ID:') or line.startswith('  - Jira ID:'):
                jira_id = line.split(':', 1)[1].strip()
            elif line.startswith('- Summary:') or line.startswith('  - Summary:'):
                summary = line.split(':', 1)[1].strip()
            elif line.startswith('- Suggested Filename:') or line.startswith('  - Suggested Filename:'):
                filename = line.split(':', 1)[1].strip()
                tickets.append((ticket_url, jira_id, summary, filename))
                ticket_url = jira_id = summary = filename = ''
    return tickets


def read_zd_csv_map(path: str) -> Dict[str, Dict[str, str]]:
    mapping: Dict[str, Dict[str, str]] = {}
    if not os.path.exists(path):
        return mapping
    with open(path, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            url = (row.get('Zendesk Ticket') or '').strip()
            if not url:
                continue
            mapping[url] = {
                'side': (row.get('UI / BE Side') or '').strip(),
                'feature': (row.get('Feature/Component') or '').strip(),
                'release': (row.get('Caused due to this release ?') or '').strip(),
                'regress': (row.get('Is this Regression /Escape Bug') or '').strip(),
            }
    return mapping


def infer_layers(side: str, summary: str, feature: str) -> List[str]:
    side_l = (side or '').lower()
    layers: List[str] = []
    if 'ui' in side_l or 'frontend' in side_l:
        layers.append('UI')
    if 'be' in side_l or 'backend' in side_l or not layers:
        layers.append('Backend')
    return layers


def build_test_cases_md(ticket: TicketInfo, meta: Dict[str, str]) -> str:
    ticket_url, jira_id, summary, filename = ticket
    side = meta.get('side', '')
    feature = meta.get('feature', '')
    release = meta.get('release', '')
    regress = meta.get('regress', '')
    layers = infer_layers(side, summary, feature)

    header = [
        f"# Zendesk {ticket_url.split('/')[-1]} — Test Cases",
        f"- Ticket: {ticket_url}",
        f"- Jira: {jira_id}",
        f"- Feature/Component: {feature or 'N/A'}",
        f"- UI/BE Side: {side or 'N/A'}",
        f"- Context: {summary}",
        "",
    ]

    def test_block(tc_id: str, title: str, test_type: str, layer: str, data: List[str]) -> str:
        steps = [
            "1) Prepare environment and prerequisites",
            "2) Execute action(s) per scenario",
            "3) Observe outputs, logs, and side effects",
        ]
        expected = [
            "- Positive: behavior matches spec without errors",
            "- Negative: clear validation or bounded retry; no crash",
            "- Edge: policy-conformant handling of extremes",
        ]
        return "\n".join([
            f"- **Test Case ID:** {tc_id}",
            f"- **Title/Description:** {title}",
            "- **Preconditions:",
            "  - Auth and configs valid; realistic data available",
            f"  - Layer: {layer}",
            "- **Test Steps:",
            *[f"  - {s}" for s in steps],
            "- **Test Data:",
            *[f"  - {d}" for d in data],
            "- **Expected Result:",
            *[f"  - {e}" for e in expected],
            "- **Actual Result:** TBD",
            "- **Status:** Not Executed",
            "- **Postconditions:** System stable; resources cleaned",
            f"- **Tags/Labels:** [regression, {layer.lower()}, escape={str(regress.lower() in ('escape','yes')).lower()}, release={str(release.lower()=='yes').lower()}]",
            f"- **Test Type:** {test_type}",
            "",
        ])

    def data_hints(layer: str) -> List[str]:
        hints: List[str] = []
        if feature:
            hints.append(f"Feature: {feature}")
        if 'multipart' in summary.lower() or 'multipart' in feature.lower():
            hints += [
                "HTTP multipart/form-data payload (boundary, parts >8MB)",
                "Concurrent uploads=5, network jitter=200ms",
            ]
        if 'timestamp' in summary.lower():
            hints += [
                "Sample records with varying timezones (UTC, PST, IST)",
                "Edge timestamps: epoch, leap second, DST transition",
            ]
        if layer == 'UI':
            hints += [
                "Browsers: Chrome/Edge/Firefox LTS",
                "User roles: admin, operator",
            ]
        else:
            hints += [
                "API endpoint: provide URL and auth",
                "Payload: representative JSON with boundary conditions",
            ]
        return hints

    parts: List[str] = header
    for layer in layers:
        parts.append(f"## {layer} Layer")
        data = data_hints(layer)
        # Regression
        parts.append(test_block(
            tc_id=f"{ticket_url.split('/')[-1]}-{layer}-REG-01",
            title="Regression: previously failing scenario does not reoccur",
            test_type="Regression",
            layer=layer,
            data=data,
        ))
        # Edge cases
        parts.append(test_block(
            tc_id=f"{ticket_url.split('/')[-1]}-{layer}-EDGE-01",
            title="Edge: extreme payloads, special characters, concurrency",
            test_type="Edge",
            layer=layer,
            data=data,
        ))
        # Error handling
        parts.append(test_block(
            tc_id=f"{ticket_url.split('/')[-1]}-{layer}-ERR-01",
            title="Error handling: timeouts, 4xx/5xx, validation failures",
            test_type="Recovery",
            layer=layer,
            data=data,
        ))
        # Functional
        parts.append(test_block(
            tc_id=f"{ticket_url.split('/')[-1]}-{layer}-FUNC-01",
            title="Functional: expected behavior for normal inputs",
            test_type="Functional",
            layer=layer,
            data=data,
        ))

    return "\n".join(parts)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    candidates = read_candidates_md(MD_INPUT)
    zd_map = read_zd_csv_map(CSV_SRC)

    written: List[str] = []
    for ticket in candidates:
        ticket_url, jira_id, summary, filename = ticket
        meta = zd_map.get(ticket_url, {})
        md = build_test_cases_md(ticket, meta)
        out_path = os.path.join(OUT_DIR, filename if filename.endswith('.md') else (filename + '.md'))
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(md)
        written.append(out_path)

    for p in written[:10]:
        print(f"Wrote: {p}")
    print(f"TOTAL_FILES={len(written)}")


if __name__ == '__main__':
    main()

