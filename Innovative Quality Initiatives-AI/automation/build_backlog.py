#!/usr/bin/env python3
import os
import re
import csv
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)

SRC_DIRS = {
    'Jira': os.path.join(ROOT, 'jira_stories'),
    'PR': os.path.join(ROOT, 'pr_test_cases'),
    'Slack': os.path.join(ROOT, 'slack_test_cases'),
}

OUT_CSV = os.path.join(BASE_DIR, 'automation_backlog.csv')
TOP25 = os.path.join(BASE_DIR, 'top25.md')
TOP50 = os.path.join(BASE_DIR, 'top50.md')

JIRA_RE = re.compile(r'\bIO-\d+\b', re.IGNORECASE)


def read_text(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        return ''


def list_tests() -> list:
    items = []
    for source, d in SRC_DIRS.items():
        if not os.path.exists(d):
            continue
        for fname in sorted(os.listdir(d)):
            if not fname.lower().endswith('.md'):
                continue
            path = os.path.join(d, fname)
            text = read_text(path)
            # split by test blocks
            blocks = []
            cur = []
            for line in text.splitlines():
                if line.strip().startswith('- Test Case ID:') and cur:
                    blocks.append('\n'.join(cur))
                    cur = [line]
                else:
                    cur.append(line)
            if cur:
                blocks.append('\n'.join(cur))
            if not blocks:
                blocks = [text]
            for b in blocks:
                tcid = ''
                m = re.search(r'-\s*Test Case ID:\s*(.+)', b)
                if m:
                    tcid = m.group(1).strip()
                layer = 'BE'
                if re.search(r'####\s*UI', text, re.IGNORECASE) or re.search(r'Layer:\s*UI', b, re.IGNORECASE):
                    layer = 'UI'
                if re.search(r'Test Type:\s*API', b, re.IGNORECASE) or 'API-parity' in b:
                    layer = 'API'
                component = 'core'
                comp_m = re.search(r'component=([^,\]\s]+)', text, re.IGNORECASE)
                if comp_m:
                    component = comp_m.group(1).strip()
                items.append({
                    'Source': source,
                    'File': fname,
                    'Path': path,
                    'Block': b,
                    'TestCaseID': tcid or os.path.splitext(fname)[0],
                    'Layer': layer,
                    'Component': component,
                })
    return items


def compute_priority(block: str, file_name: str, source: str) -> int:
    t = (block or '').lower()
    sev = 0
    if 'sev=p0' in t or ' p0 ' in t:
        sev = 5
    elif 'sev=p1' in t or ' p1 ' in t:
        sev = 3
    elif 'sev=p2' in t or ' p2 ' in t:
        sev = 1
    prod = 3 if 'prod=true' in t else 0
    customer_touch = 2 if any(k in t for k in ['ui', 'dashboard', 'permissions', 'rbac']) else 0
    change_recent = 2 if source == 'PR' else 0
    escaped = 2 if any(k in t for k in ['escape', 'escaped', 'regression']) else 0
    bonus = 0
    if 'performance' in t or 'load' in t:
        bonus += 1
    if 'a11y' in t or 'accessibility' in t:
        bonus += 1
    if 'security' in t or 'rbac' in t:
        bonus += 1
    return sev + prod + customer_touch + change_recent + escaped + bonus


def estimation(score: int) -> str:
    if score >= 9:
        return 'L'
    if score >= 6:
        return 'M'
    return 'S'


def write_backlog(rows: list) -> None:
    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Source', 'TestCaseID', 'File', 'Layer', 'Component', 'PriorityScore', 'Est', 'Owner', 'Jira/PR/SlackRef'])
        for r in rows:
            w.writerow([
                r['Source'], r['TestCaseID'], r['File'], r['Layer'], r['Component'], r['PriorityScore'], r['Est'], '', r['Ref']
            ])


def write_top_md(rows: list, path: str, n: int) -> None:
    lines = []
    lines.append(f'### Top {n} Automation Candidates')
    lines.append('')
    lines.append('Rank | Score | Source | TestCaseID | File | Layer | Component')
    lines.append('---|---:|---|---|---|---|---')
    for i, r in enumerate(rows[:n], start=1):
        lines.append(f"{i} | {r['PriorityScore']} | {r['Source']} | {r['TestCaseID']} | {r['File']} | {r['Layer']} | {r['Component']}")
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    items = list_tests()
    rows = []
    for it in items:
        score = compute_priority(it['Block'], it['File'], it['Source'])
        ref = ''
        if it['Source'] == 'Jira':
            m = JIRA_RE.search(read_text(it['Path']))
            ref = m.group(0).upper() if m else ''
        elif it['Source'] == 'PR':
            m = re.search(r'PR-(\d+)', it['File'])
            ref = f"PR-{m.group(1)}" if m else ''
        elif it['Source'] == 'Slack':
            m = re.search(r'SLK-(.+)\.md$', it['File'])
            ref = m.group(1) if m else ''
        rows.append({
            'Source': it['Source'],
            'TestCaseID': it['TestCaseID'],
            'File': it['File'],
            'Layer': it['Layer'],
            'Component': it['Component'],
            'PriorityScore': score,
            'Est': estimation(score),
            'Ref': ref,
        })
    rows.sort(key=lambda r: r['PriorityScore'], reverse=True)
    write_backlog(rows)
    write_top_md(rows, TOP25, 25)
    write_top_md(rows, TOP50, 50)
    print(f'SAVED: {OUT_CSV}')
    print(f'SAVED: {TOP25}')
    print(f'SAVED: {TOP50}')
    # Print top 10
    print('TOP10:')
    for r in rows[:10]:
        print(f"{r['PriorityScore']} | {r['Source']} | {r['TestCaseID']} | {r['File']} | {r['Layer']} | {r['Component']}")


if __name__ == '__main__':
    main()



