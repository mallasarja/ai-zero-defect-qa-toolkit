#!/usr/bin/env python3
import os
import csv
import re
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)

ACC_CSV = os.path.join(ROOT, 'validation', 'batch_accuracy_summary.csv')
BACKLOG_CSV = os.path.join(ROOT, 'automation', 'automation_backlog.csv')
SLACK_DEDUP = os.path.join(ROOT, 'slack_test_cases', 'DEDUP_REPORT.md')
COVERAGE_MD = os.path.join(ROOT, 'io_story_test_coverage_summary.md')
SLACK_NORM = os.path.join(ROOT, 'slack_e2e', 'normalized.csv')
PR_READY = os.path.join(ROOT, 'ready_prs_last_90d.csv')

QUALITY_DASHBOARD = os.path.join(BASE_DIR, 'quality_dashboard.md')
LEADERSHIP_ONEPAGER = os.path.join(BASE_DIR, 'leadership_onepager.md')


def safe_float(s: str) -> float:
    try:
        return float(s)
    except Exception:
        return 0.0


def read_batch_accuracy(csv_path: str):
    data = []
    if not os.path.exists(csv_path):
        return {
            'avg_score30': 0.0,
            'avg_score_pct': 0.0,
            'total_manual': 0,
            'total_ai': 0,
        }
    with open(csv_path, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            data.append(row)
    total_manual = sum(int(row.get('ManualCount') or 0) for row in data)
    total_ai = sum(int(row.get('AICount') or 0) for row in data)
    scores30 = [safe_float(row.get('Score/30') or 0.0) for row in data]
    scorespct = [safe_float(row.get('Score%') or 0.0) for row in data]
    avg30 = round(sum(scores30) / len(scores30), 2) if scores30 else 0.0
    avgpct = round(sum(scorespct) / len(scorespct), 1) if scorespct else 0.0
    return {
        'avg_score30': avg30,
        'avg_score_pct': avgpct,
        'total_manual': total_manual,
        'total_ai': total_ai,
    }


def parse_slack_dedup(md_path: str):
    counts = {'NEW': 0, 'EXTENDS': 0, 'DUPLICATE': 0}
    if not os.path.exists(md_path):
        return counts
    with open(md_path, 'r', encoding='utf-8') as f:
        for line in f:
            m = re.match(r'-\s*(NEW|EXTENDS|DUPLICATE):\s*(\d+)', line.strip())
            if m:
                counts[m.group(1)] = int(m.group(2))
    return counts


def read_backlog(csv_path: str):
    rows = []
    if not os.path.exists(csv_path):
        return rows
    with open(csv_path, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows


def top_components(backlog_rows, top_n=5):
    counts = {}
    for r in backlog_rows:
        comp = (r.get('Component') or 'core').strip()
        counts[comp] = counts.get(comp, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]


def a11y_sec_perf_counts(backlog_rows):
    a11y = sec = perf = 0
    for r in backlog_rows:
        file = r.get('File') or ''
        # Infer by Test Type or file hints
        if 'a11y' in file.lower():
            a11y += 1
        tt = (r.get('Layer') or '') + ' ' + (r.get('File') or '')
        s = tt.lower()
        if 'security' in s or 'rbac' in s:
            sec += 1
        if 'perf' in s or 'performance' in s or 'load' in s:
            perf += 1
    return a11y, sec, perf


def weekly_trend_slack(norm_csv: str):
    buckets = {}
    if not os.path.exists(norm_csv):
        return buckets
    with open(norm_csv, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            dt = row.get('last_seen_at') or ''
            try:
                d = datetime.fromisoformat(dt)
                year_week = f"{d.isocalendar().year}-W{d.isocalendar().week:02d}"
                buckets[year_week] = buckets.get(year_week, 0) + 1
            except Exception:
                continue
    return dict(sorted(buckets.items()))


def weekly_trend_pr(pr_csv: str):
    buckets = {}
    if not os.path.exists(pr_csv):
        return buckets
    with open(pr_csv, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            dt = (row.get('created_at') or '').replace('Z', '')
            try:
                d = datetime.fromisoformat(dt)
                year_week = f"{d.isocalendar().year}-W{d.isocalendar().week:02d}"
                buckets[year_week] = buckets.get(year_week, 0) + 1
            except Exception:
                continue
    return dict(sorted(buckets.items()))


def write_quality_dashboard(acc, slack_counts, backlog_rows, trend_slack, trend_pr):
    coverage_pct = round(100.0 * acc['total_ai'] / max(1, acc['total_manual']), 1) if acc['total_manual'] else 0.0
    comps = top_components(backlog_rows)
    a11y, sec, perf = a11y_sec_perf_counts(backlog_rows)
    lines = []
    lines.append('### Overall KPIs (Build)')
    lines.append('')
    lines.append(f"- AI vs Manual Avg Score/30: {acc['avg_score30']}")
    lines.append(f"- AI vs Manual Avg Score%: {acc['avg_score_pct']}%")
    lines.append(f"- Coverage (AI/Manual): {acc['total_ai']}/{acc['total_manual']} = {coverage_pct}%")
    lines.append(f"- Slack NEW/EXTENDS/DUPLICATE: {slack_counts.get('NEW',0)}/{slack_counts.get('EXTENDS',0)}/{slack_counts.get('DUPLICATE',0)}")
    lines.append('- Top components: ' + ', '.join([f"{k}({v})" for k, v in comps]))
    lines.append(f'- A11y/Security/Perf counts: {a11y}/{sec}/{perf}')
    lines.append('')
    if trend_slack or trend_pr:
        lines.append('Weekly Trend (Slack threads | PRs)')
        weeks = sorted(set(list(trend_slack.keys()) + list(trend_pr.keys())))
        lines.append('Week | Slack | PRs')
        lines.append('---|---:|---:')
        for w in weeks[-12:]:
            lines.append(f"{w} | {trend_slack.get(w,0)} | {trend_pr.get(w,0)}")
        lines.append('')
    with open(QUALITY_DASHBOARD, 'a', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'SAVED: {QUALITY_DASHBOARD}')


def write_leadership_onepager(acc, slack_counts, backlog_rows):
    coverage_pct = round(100.0 * acc['total_ai'] / max(1, acc['total_manual']), 1) if acc['total_manual'] else 0.0
    comps = top_components(backlog_rows)
    a11y, sec, perf = a11y_sec_perf_counts(backlog_rows)
    lines = []
    lines.append('### Leadership One-Pager')
    lines.append('')
    # 3 bullets
    lines.append(f'- AI vs Manual average score is {acc["avg_score30"]}/30 ({acc["avg_score_pct"]}%). Coverage is {coverage_pct}%.')
    lines.append(f'- Slack-derived tests: NEW/EXTENDS/DUPLICATE = {slack_counts.get("NEW",0)}/{slack_counts.get("EXTENDS",0)}/{slack_counts.get("DUPLICATE",0)}; Top components: ' + ', '.join([f"{k}({v})" for k,v in comps]))
    lines.append(f'- A11y/Security/Performance tests: {a11y}/{sec}/{perf}.')
    lines.append('')
    # 1 table
    lines.append('Metric | Value')
    lines.append('---|---:')
    lines.append(f"Avg Score/30 | {acc['avg_score30']}")
    lines.append(f"Avg Score% | {acc['avg_score_pct']}%")
    lines.append(f"Coverage (AI/Manual) | {coverage_pct}%")
    lines.append(f"Slack NEW | {slack_counts.get('NEW',0)}")
    lines.append(f"Slack EXTENDS | {slack_counts.get('EXTENDS',0)}")
    lines.append(f"Slack DUPLICATE | {slack_counts.get('DUPLICATE',0)}")
    lines.append(f"Top components | {', '.join([f'{k}({v})' for k,v in comps])}")
    lines.append(f"A11y/Security/Perf | {a11y}/{sec}/{perf}")
    lines.append('')
    # 1 call-to-action
    lines.append('Call to Action: Focus automation on top-25 backlog (High scores, Slack NEW/EXTENDS) and validate a11y/security/perf gaps.')
    lines.append('')
    with open(LEADERSHIP_ONEPAGER, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'SAVED: {LEADERSHIP_ONEPAGER}')


def main():
    acc = read_batch_accuracy(ACC_CSV)
    slack_counts = parse_slack_dedup(SLACK_DEDUP)
    backlog_rows = read_backlog(BACKLOG_CSV)
    trend_slack = weekly_trend_slack(SLACK_NORM)
    trend_pr = weekly_trend_pr(PR_READY)
    write_quality_dashboard(acc, slack_counts, backlog_rows, trend_slack, trend_pr)
    write_leadership_onepager(acc, slack_counts, backlog_rows)


if __name__ == '__main__':
    main()





