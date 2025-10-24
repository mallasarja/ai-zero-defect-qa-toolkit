#!/usr/bin/env python3
import csv
import json
import os
from collections import Counter, defaultdict
from datetime import datetime


PUBLIC_DIR = os.path.join(os.path.dirname(__file__), 'public')
JOIN_CSV = os.path.join(PUBLIC_DIR, 'bug_with_pr_link.csv')
OUT_JSON = os.path.join(PUBLIC_DIR, 'bug_metrics_dashboard.json')
SEVERITY_CSV = os.path.join(PUBLIC_DIR, 'bug_severity_distribution.csv')
PRIORITY_CSV = os.path.join(PUBLIC_DIR, 'bug_priority_distribution.csv')
RELEASE_TREND_CSV = os.path.join(PUBLIC_DIR, 'bug_trend_releasewise.csv')


def parse_datetime(dt_str: str):
    if not dt_str:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    return None


def is_truthy(v) -> bool:
    if v is None:
        return False
    s = str(v).strip().lower()
    return s in ("true", "yes", "1")


def read_rows(path: str):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def compute_metrics_and_distributions():
    total_bugs = 0
    escaped_bugs = 0
    pr_linked_bugs = 0
    mttr_days_values = []

    severity_counter = Counter()
    priority_counter = Counter()
    release_counter = Counter()

    # Attempt to detect a release column
    # Common options: 'Fix Version', 'Fix Versions', 'release', 'Release'
    with open(JOIN_CSV, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, [])
    header_lower = [h.lower() for h in header]
    release_col_name = None
    for candidate in ("Fix Version", "Fix Versions", "release", "Release"):
        if candidate.lower() in header_lower:
            release_col_name = candidate
            break

    for row in read_rows(JOIN_CSV):
        total_bugs += 1

        if is_truthy(row.get('is_escaped_defect')):
            escaped_bugs += 1

        if (row.get('linked_pr_number') or '').strip():
            pr_linked_bugs += 1

        sev = (row.get('severity') or '').strip() or 'Unspecified'
        priority = (row.get('priority') or '').strip() or 'Unspecified'
        severity_counter[sev] += 1
        priority_counter[priority] += 1

        if release_col_name:
            rel_val = (row.get(release_col_name) or '').strip()
            if rel_val:
                # Some Jira exports can have multiple versions separated by ';'
                parts = [p.strip() for p in rel_val.replace('|', ';').split(';') if p.strip()]
                if parts:
                    for p in parts:
                        release_counter[p] += 1
                else:
                    release_counter['Unknown'] += 1
            else:
                release_counter['Unknown'] += 1

        created = parse_datetime(row.get('created') or '')
        resolved = parse_datetime(row.get('resolved') or '')
        if created and resolved:
            delta = resolved - created
            mttr_days_values.append(delta.total_seconds() / 86400.0)

    avg_mttr = round(sum(mttr_days_values) / len(mttr_days_values), 2) if mttr_days_values else 0.0

    return {
        'total_bugs': total_bugs,
        'escaped_bugs': escaped_bugs,
        'pr_linked_bugs': pr_linked_bugs,
        'avg_mttr': avg_mttr,
    }, severity_counter, priority_counter, release_counter, bool(release_col_name)


def write_json_metrics(metrics: dict):
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)


def write_distribution_csv(path: str, header: str, counter: Counter):
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([header, 'count'])
        for key, count in sorted(counter.items(), key=lambda kv: (-kv[1], str(kv[0]))):
            w.writerow([key, count])


def main():
    if not os.path.exists(JOIN_CSV):
        raise FileNotFoundError(f"Input CSV not found: {JOIN_CSV}")

    metrics, sev_counter, pri_counter, rel_counter, have_release = compute_metrics_and_distributions()
    write_json_metrics(metrics)
    write_distribution_csv(SEVERITY_CSV, 'severity', sev_counter)
    write_distribution_csv(PRIORITY_CSV, 'priority', pri_counter)

    # Only write release-wise trend if a release column was found; otherwise fallback to month grouping
    if have_release and rel_counter:
        write_distribution_csv(RELEASE_TREND_CSV, 'release', rel_counter)
    else:
        # Fallback: group by created month as pseudo-release to ensure chart renders
        month_counter = Counter()
        for row in read_rows(JOIN_CSV):
            dt = parse_datetime(row.get('created') or '')
            if not dt:
                continue
            key = f"{dt.year}-{str(dt.month).zfill(2)}"
            month_counter[key] += 1
        write_distribution_csv(RELEASE_TREND_CSV, 'release', month_counter)

    print(f"Saved metrics to: {OUT_JSON}")
    print(f"Saved severity distribution to: {SEVERITY_CSV}")
    print(f"Saved priority distribution to: {PRIORITY_CSV}")
    print(f"Saved release trend to: {RELEASE_TREND_CSV}")


if __name__ == '__main__':
    main()

