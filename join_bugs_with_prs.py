#!/usr/bin/env python3
import csv
import os
import re
from collections import defaultdict


PUBLIC_DIR = os.path.join(os.path.dirname(__file__), 'public')
BUGS_CSV = os.path.join(PUBLIC_DIR, 'mcp_jira_bugs.csv')
PRS_CSV = os.path.join(PUBLIC_DIR, 'github_prs.csv')
OUT_JOIN_CSV = os.path.join(PUBLIC_DIR, 'bug_with_pr_link.csv')


def load_pr_index_by_issue_key():
    """Index PR numbers by detected issue key within PR title.
    Looks for patterns like ABC-123 in the PR title.
    """
    if not os.path.exists(PRS_CSV):
        return {}

    issue_to_prs = defaultdict(list)
    with open(PRS_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = (row.get('title') or '').strip()
            pr_number = (row.get('pr_number') or '').strip()
            if not title or not pr_number:
                continue
            for match in re.findall(r'[A-Z]{2,}-\d+', title):
                issue_to_prs[match].append(pr_number)
    return issue_to_prs


def main():
    if not os.path.exists(BUGS_CSV):
        raise FileNotFoundError(f"Bugs CSV not found: {BUGS_CSV}")

    issue_to_prs = load_pr_index_by_issue_key()

    with open(BUGS_CSV, newline='', encoding='utf-8') as f_in, open(OUT_JOIN_CSV, 'w', newline='', encoding='utf-8') as f_out:
        reader = csv.DictReader(f_in)
        fieldnames = list(reader.fieldnames or [])
        if 'linked_pr_number' not in fieldnames:
            fieldnames.append('linked_pr_number')
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            key = (row.get('issueKey') or '').strip()
            prs = issue_to_prs.get(key, [])
            row['linked_pr_number'] = ','.join(sorted(set(prs))) if prs else ''
            writer.writerow(row)

    print(f"Wrote joined CSV: {OUT_JOIN_CSV}")


if __name__ == '__main__':
    main()


