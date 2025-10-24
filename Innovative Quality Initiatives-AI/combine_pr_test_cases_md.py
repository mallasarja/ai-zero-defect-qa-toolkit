#!/usr/bin/env python3
from __future__ import annotations

import os
import re

BASE_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.join(BASE_DIR, 'pr_test_cases')
OUT_MD = os.path.join(BASE_DIR, 'pr_test_cases_all.md')


def pr_number_from_filename(name: str) -> int:
    m = re.search(r'PR-(\d+)_structured_test_cases\.md$', name)
    return int(m.group(1)) if m else 0


def main() -> None:
    if not os.path.isdir(SRC_DIR):
        print(f"Source folder not found: {SRC_DIR}")
        return

    files = [f for f in os.listdir(SRC_DIR) if f.endswith('_structured_test_cases.md')]
    files.sort(key=pr_number_from_filename, reverse=True)

    parts = [
        "# PR Test Cases — Combined Report\n",
        "This report aggregates structured test cases for all recent PRs.\n",
        "\n## Table of Contents\n",
    ]

    for fname in files:
        num = pr_number_from_filename(fname)
        parts.append(f"- [PR #{num}](#pr-{num})")
    parts.append("\n")

    for fname in files:
        num = pr_number_from_filename(fname)
        parts.append(f"\n---\n\n<a id=\"pr-{num}\"></a>")
        src_path = os.path.join(SRC_DIR, fname)
        with open(src_path, 'r', encoding='utf-8') as f:
            content = f.read()
        parts.append(content)

    with open(OUT_MD, 'w', encoding='utf-8') as f:
        f.write("\n".join(parts))

    print(OUT_MD)


if __name__ == '__main__':
    main()

