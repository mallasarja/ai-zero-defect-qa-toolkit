#!/usr/bin/env python3
import os
import json
import csv
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')
ZENDESK_CLEANED = os.path.join(BASE_DIR, 'cleaned_zendesk_issues.csv')
ZEPHYR_TESTS = os.path.join(PUBLIC_DIR, 'zephyr_tests.csv')
BUG_WITH_PR = os.path.join(PUBLIC_DIR, 'bug_with_pr_link.csv')


def ensure_public_dir():
    os.makedirs(PUBLIC_DIR, exist_ok=True)


def parse_date_safe(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s))
    except Exception:
        # try common formats
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(str(s), fmt)
            except Exception:
                continue
    return None


def month_key(dt: datetime) -> str:
    return f"{dt.year}-{str(dt.month).zfill(2)}"


def interpret_automation_status(value: str) -> bool:
    s = (value or '').strip().lower()
    # Treat any value containing 'automated' as automated
    if 'automated' in s:
        return True
    # Explicit allowlist (case-insensitive exact match)
    automated_values = {
        'api automated',
        'automated',
        'automated via unit test',
        'to be automated api',
        'to be automated ui',
        'to be automated ui unit test',
    }
    if s in automated_values:
        return True
    # Explicit denylist (manual / non-automated)
    manual_values = {
        'manual',
        'not applicable',
        'one_time testcase',
        'blocked',
    }
    if s in manual_values:
        return False
    return False


def generate_automation_coverage() -> dict:
    """Compute automation coverage using zephyr_tests.csv and map Automation_Status values."""
    coverage_percent = None
    coverage_by_module = []
    defects_missed = []

    if not os.path.exists(ZEPHYR_TESTS):
        return {
            "automation_coverage_percent": coverage_percent,
            "coverage_by_module": coverage_by_module,
            "defects_missed": defects_missed,
        }

    total = 0
    automated = 0
    module_to_total = {}
    module_to_auto = {}

    # Load tests and determine automation flags
    tests: list[dict] = []
    with open(ZEPHYR_TESTS, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            module = (row.get('component') or '-').strip() or '-'
            auto_status = row.get('Automation_Status') or row.get('automation_status')
            if auto_status is None:
                # fallback to previous 'automated' Yes/No column
                auto_status = 'Automated' if (row.get('automated') or '').strip().lower() in ('yes', 'true', '1') else 'Manual'
            is_auto = interpret_automation_status(auto_status)
            tests.append({
                'module': module,
                'summary': row.get('summary') or '',
                'labels': row.get('labels') or '',
                'is_auto': is_auto,
                'automation_status': auto_status,
            })
            total += 1
            module_to_total[module] = module_to_total.get(module, 0) + 1
            if is_auto:
                automated += 1
                module_to_auto[module] = module_to_auto.get(module, 0) + 1

    if total > 0:
        coverage_percent = round((automated / total) * 100, 1)
    for module, count in sorted(module_to_total.items(), key=lambda kv: (-kv[1], kv[0])):
        auto = module_to_auto.get(module, 0)
        pct = round((auto / count) * 100, 1) if count else 0.0
        coverage_by_module.append({
            "module": module,
            "coverage_percent": pct,
            "total": count,
            "automated": auto,
        })

    # Compute escaped defects that have no automated test referencing their key
    escaped_without_auto: list[dict] = []
    bug_path = BUG_WITH_PR
    if os.path.exists(bug_path):
        with open(bug_path, newline='', encoding='utf-8') as bf:
            bug_reader = csv.DictReader(bf)
            for brow in bug_reader:
                escaped_flag = str(brow.get('escapedDefect') or '').strip().lower() in ('true', 'yes', '1')
                if not escaped_flag:
                    continue
                issue_key = (brow.get('issueKey') or '').strip()
                if not issue_key:
                    continue
                # Find any automated test that references this issue key in summary or labels
                has_auto = any(t['is_auto'] and (issue_key.lower() in (t['summary'] or '').lower() or issue_key.lower() in (t['labels'] or '').lower()) for t in tests)
                if not has_auto:
                    escaped_without_auto.append({
                        'issueKey': issue_key,
                        'summary': brow.get('summary') or '',
                        'created': brow.get('created') or '',
                        'resolved': brow.get('resolved') or '',
                        'status': brow.get('status') or '',
                        'severity': brow.get('severity') or '',
                        'escapedDefect': brow.get('escapedDefect') or '',
                        'linked_pr_number': brow.get('linked_pr_number') or '',
                    })

    # Write escaped_without_ai_tests.csv reflecting no automated tests present
    if escaped_without_auto:
        out_csv = os.path.join(PUBLIC_DIR, 'escaped_without_ai_tests.csv')
        headers = ['issueKey','summary','created','resolved','status','severity','escapedDefect','linked_pr_number']
        with open(out_csv, 'w', newline='', encoding='utf-8') as outf:
            w = csv.DictWriter(outf, fieldnames=headers)
            w.writeheader()
            for r in escaped_without_auto:
                w.writerow(r)

    return {
        "automation_coverage_percent": coverage_percent,
        "coverage_by_module": coverage_by_module,
        "defects_missed": escaped_without_auto,
    }


def generate_ai_testing_impact() -> dict:
    """Placeholder AI testing impact. If future data source exists, ingest it here."""
    # Without a concrete data source, emit an empty baseline structure
    return {
        "ai_tests_generated_count": None,
        "ai_usage_by_month": [],
        "coverage_improvement_percent": None,
        "customer_satisfaction_trend": [],
        "customer_issues_by_month": [],
    }


def main():
    ensure_public_dir()
    auto = generate_automation_coverage()

    with open(os.path.join(PUBLIC_DIR, 'automation_coverage.json'), 'w', encoding='utf-8') as f:
        json.dump(auto, f, ensure_ascii=False, indent=2)

    # Do not overwrite existing AI impact if already generated elsewhere
    ai_path = os.path.join(PUBLIC_DIR, 'ai_testing_impact.json')
    if not os.path.exists(ai_path):
        ai = generate_ai_testing_impact()
        with open(ai_path, 'w', encoding='utf-8') as f:
            json.dump(ai, f, ensure_ascii=False, indent=2)

    print("Saved:")
    print(os.path.join(PUBLIC_DIR, 'automation_coverage.json'))
    if os.path.exists(ai_path):
        print(ai_path)


if __name__ == '__main__':
    main()

