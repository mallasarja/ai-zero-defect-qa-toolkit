#!/usr/bin/env python3
import csv
import os
from collections import defaultdict


BASE_DIR = os.path.dirname(__file__)
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')
INPUT_CSV = os.path.join(PUBLIC_DIR, 'mcp_jira_bugs.csv')
OUTPUT_CSV = os.path.join(PUBLIC_DIR, 'bug_trend_releasewise.csv')


def split_fix_versions(value: str):
    if not value:
        return []
    raw = str(value).strip()
    if not raw:
        return []
    # Try to normalize simple JSON-ish lists like ["1.0","1.1"]
    if raw.startswith('[') and raw.endswith(']'):
        raw = raw.strip('[]')
        parts = [p.strip().strip('"\'') for p in raw.split(',')]
        return [p for p in parts if p]
    # Otherwise, split on common delimiters
    seps = [';', '|', ',', '\n']
    parts = [raw]
    for sep in seps:
        parts = sum([p.split(sep) for p in parts], [])
    return [p.strip() for p in parts if p and p.strip()]


def find_fix_versions_key(header):
    candidates = ['Fix Versions', 'Fix Version', 'fixVersions', 'Fix versions', 'FixVersion']
    lower = {h.lower(): h for h in header}
    for c in candidates:
        if c.lower() in lower:
            return lower[c.lower()]
    return None


def main():
    if not os.path.exists(INPUT_CSV):
        raise FileNotFoundError(f"Input not found: {INPUT_CSV}")

    with open(INPUT_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        fix_key = find_fix_versions_key(header)

        # Counters grouped by (fix_version, severity, priority)
        counts = defaultdict(int)

        for row in reader:
            severity = (row.get('severity') or row.get('Severity') or '').strip() or 'Unspecified'
            priority = (row.get('priority') or row.get('Priority') or '').strip() or 'Unspecified'

            fixes = []
            if fix_key:
                fixes = split_fix_versions(row.get(fix_key) or '')
            if not fixes:
                fixes = ['Unknown']

            for fv in fixes:
                counts[(fv, severity, priority)] += 1

    os.makedirs(PUBLIC_DIR, exist_ok=True)
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(['Fix Versions', 'Severity', 'Priority', 'Bug Count'])
        for (fv, sev, pri) in sorted(counts.keys(), key=lambda k: (str(k[0]), str(k[1]), str(k[2]))):
            writer.writerow([fv, sev, pri, counts[(fv, sev, pri)]])

    print(f"Saved: {OUTPUT_CSV}")


if __name__ == '__main__':
    main()

