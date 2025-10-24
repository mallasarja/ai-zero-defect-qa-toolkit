#!/usr/bin/env python3
import csv
import json
import os
from datetime import datetime


def parse_datetime(dt_str: str):
    if not dt_str:
        return None
    # Jira style: 2015-04-16T15:04:38.133+0530
    # Some rows may not have milliseconds; try multiple formats
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    return None


def is_truthy(v):
    if v is None:
        return False
    s = str(v).strip().lower()
    return s in ("true", "yes", "1")


def compute_metrics(csv_path: str):
    total_bugs = 0
    escaped_bugs = 0
    pr_linked_bugs = 0
    mttr_days_values = []

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_bugs += 1

            if is_truthy(row.get('escapedDefect')):
                escaped_bugs += 1

            linked_pr = (row.get('linkedPR') or '').strip()
            if linked_pr:
                pr_linked_bugs += 1

            created = parse_datetime(row.get('created') or '')
            resolved = parse_datetime(row.get('resolved') or '')
            if created and resolved:
                delta = resolved - created
                mttr_days_values.append(delta.total_seconds() / 86400.0)

    avg_mttr = round(sum(mttr_days_values) / len(mttr_days_values), 2) if mttr_days_values else 0.0

    return {
        "total_bugs": total_bugs,
        "escaped_bugs": escaped_bugs,
        "pr_linked_bugs": pr_linked_bugs,
        "avg_mttr": avg_mttr,
    }


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    public_dir = os.path.join(base_dir, 'public')
    input_csv = os.path.join(public_dir, 'mcv_jira_bugs.csv')
    output_json = os.path.join(public_dir, 'bug_metrics_dashboard.json')

    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    metrics = compute_metrics(input_csv)

    with open(output_json, 'w', encoding='utf-8') as out:
        json.dump(metrics, out, ensure_ascii=False, indent=2)

    print(f"Saved metrics to: {output_json}")


if __name__ == '__main__':
    main()

