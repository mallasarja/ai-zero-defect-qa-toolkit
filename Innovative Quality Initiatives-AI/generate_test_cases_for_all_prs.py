#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import csv
from typing import List

# Ensure we can import sibling module
THIS_DIR = os.path.dirname(__file__)
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

from generate_test_cases_for_pr import get_env, fetch_pr, write_markdown  # type: ignore


def main() -> None:
    csv_path = os.path.join(os.path.dirname(__file__), 'ready_prs_last_90d.csv')
    outdir = os.path.join(os.path.dirname(__file__), 'pr_test_cases')
    os.makedirs(outdir, exist_ok=True)

    token = get_env('GITHUB_TOKEN')
    owner = 'celigo'
    repo = 'celigo-qa-automation'

    pr_numbers: List[int] = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            num = row.get('pr_number') or ''
            if num.isdigit():
                pr_numbers.append(int(num))

    for i, number in enumerate(pr_numbers, start=1):
        pr = fetch_pr(owner, repo, number, token)
        out = os.path.join(outdir, f'PR-{number}_structured_test_cases.md')
        write_markdown(pr, out)
        print(f'[{i}/{len(pr_numbers)}] Wrote {out}')


if __name__ == '__main__':
    main()

