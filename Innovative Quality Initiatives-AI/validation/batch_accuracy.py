#!/usr/bin/env python3
import os
import re
import csv
import sys
from difflib import SequenceMatcher
from collections import defaultdict, Counter


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)

IDS_FILE = os.path.join(BASE_DIR, 'story_ids.txt')

MANUAL_DIR = os.path.join(ROOT, 'manual_tests')
AI_DIRS = [
    os.path.join(ROOT, 'jira_stories'),
    os.path.join(ROOT, 'pr_test_cases'),
    os.path.join(ROOT, 'slack_test_cases'),
]

REPORT_MD = os.path.join(BASE_DIR, 'batch_accuracy_report.md')
SUMMARY_CSV = os.path.join(BASE_DIR, 'batch_accuracy_summary.csv')


def ensure_dirs():
    os.makedirs(BASE_DIR, exist_ok=True)


def read_ids(path):
    ids = []
    if not os.path.exists(path):
        return ids
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            key = line.strip()
            if not key:
                continue
            ids.append(key)
    return ids


def read_text(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        return ''


def list_files(directory):
    files = []
    if not os.path.exists(directory):
        return files
    for root, _dirs, fs in os.walk(directory):
        for f in fs:
            if f.lower().endswith(('.md', '.markdown', '.txt', '.json')):
                files.append(os.path.join(root, f))
    return files


def similarity(a: str, b: str) -> float:
    a = (a or '').strip().lower()
    b = (b or '').strip().lower()
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def extract_title(text: str) -> str:
    for line in text.splitlines():
        if line.strip().startswith('#'):
            return line.strip('# ').strip()
    return text.splitlines()[0].strip() if text.splitlines() else ''


def extract_steps(text: str):
    steps = []
    in_steps = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith('- Test Steps:'):
            in_steps = True
            continue
        if in_steps and s.startswith('- '):
            steps.append(s.strip('- ').strip())
        if in_steps and s.startswith('- Test Data:'):
            in_steps = False
    # Fallback: generic bullets
    if not steps:
        for line in text.splitlines():
            s = line.strip()
            if s.startswith('- '):
                steps.append(s.strip('- ').strip())
    return steps


def extract_ac(text: str) -> str:
    ac_lines = []
    for line in text.splitlines():
        s = line.strip()
        if s.lower().startswith('ac-') or 'Acceptance Criteria' in s:
            ac_lines.append(s)
    return ' '.join(ac_lines)


IO_VERBS = [
    'Create Flow', 'Configure Import/Export', 'Set Mappings', 'Run Flow',
    'Check Dashboard & Logs', 'Inspect HTTP/Error payloads'
]

NEG_EDGE_KEYS = [
    'negative', 'invalid', 'error', 'fail', 'edge', 'boundary', 'null', 'unicode', 'long string', 'timeout'
]

CAT_KEYS = {
    'A11y': ['a11y', 'accessibility', 'keyboard', 'focus', 'aria', 'contrast'],
    'Integration': ['integration', 'webhook', 'external', 'dependency'],
    'API-parity': ['api-parity', 'parity', 'config vs ui'],
    'Performance/Load': ['performance', 'load', 'throughput', 'latency'],
    'Security': ['security', 'rbac', 'permission', 'auth'],
    'Reliability/Recovery': ['recovery', 'restart', 'resume', 'idempotent'],
    'E2E': ['e2e', 'end-to-end', 'flow'],
    'Compatibility': ['compatibility', 'version', 'unicode'],
    'Error handling': ['error handling', 'graceful', 'retry', 'backoff']
}


def score_io_verbs(text: str) -> float:
    count = 0
    for v in IO_VERBS:
        if v.lower() in (text or '').lower():
            count += 1
    return round(3.0 * count / max(1, len(IO_VERBS)), 2)


def score_negative_edge(text: str) -> float:
    t = (text or '').lower()
    hits = sum(1 for k in NEG_EDGE_KEYS if k in t)
    return 2.0 if hits >= 2 else (1.0 if hits >= 1 else 0.0)


def category_presence(text: str):
    t = (text or '').lower()
    present = set()
    for cat, keys in CAT_KEYS.items():
        if any(k in t for k in keys):
            present.add(cat)
    return present


def find_matching_files(id_key: str, directories):
    id_lower = id_key.lower()
    matches = []
    # First pass: filepath contains key
    for d in directories:
        for path in list_files(d):
            if id_lower in os.path.basename(path).lower():
                matches.append(path)
    if matches:
        return sorted(set(matches))
    # Second pass: content contains key
    for d in directories:
        for path in list_files(d):
            text = read_text(path)
            if id_key.lower() in text.lower():
                matches.append(path)
    return sorted(set(matches))


def classify_ai_vs_manual(ai_text: str, manual_text: str):
    ai_title = extract_title(ai_text)
    ai_steps = extract_steps(ai_text)
    ai_ac = extract_ac(ai_text)

    man_title = extract_title(manual_text)
    man_steps = extract_steps(manual_text)
    man_ac = extract_ac(manual_text)

    title_sim = similarity(ai_title, man_title or manual_text)
    steps_sim = similarity(' '.join(ai_steps), ' '.join(man_steps) or manual_text)
    ac_sim = similarity(ai_ac, man_ac or manual_text)

    io_score = score_io_verbs(' '.join(ai_steps))
    neg_edge_score = score_negative_edge(ai_text)

    # 30-point rubric
    score = round(title_sim * 10 + steps_sim * 10 + ac_sim * 5 + io_score + neg_edge_score, 2)

    # Category comparison for EXTENDS
    ai_cats = category_presence(ai_text)
    man_cats = category_presence(manual_text)
    adds_value = len(ai_cats - man_cats) > 0 or neg_edge_score > 0.0

    if max(title_sim, steps_sim, ac_sim) >= 0.90:
        cls = 'DUPLICATE'
        reason = 'high similarity'
    elif max(title_sim, steps_sim, ac_sim) >= 0.80 and adds_value:
        cls = 'EXTENDS'
        reason = 'extends categories or negative/edge'
    elif max(title_sim, steps_sim, ac_sim) >= 0.80:
        cls = 'DUPLICATE'
        reason = 'similar but no added value'
    else:
        cls = 'NEW'
        reason = 'no close match'

    return cls, score, {
        'title_sim': round(title_sim, 3),
        'steps_sim': round(steps_sim, 3),
        'ac_sim': round(ac_sim, 3),
        'io_score': io_score,
        'neg_edge_score': neg_edge_score,
        'ai_cats': sorted(ai_cats),
        'man_cats': sorted(man_cats),
        'reason': reason,
    }


def parse_ai_cases(path: str):
    text = read_text(path)
    cases = []
    # Try to split by structured cases
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
    # If no structured cases, treat whole file as one case
    if len(blocks) <= 1 and '- Test Case ID:' not in text:
        blocks = [text]
    for b in blocks:
        cases.append({'path': path, 'text': b})
    return cases


def analyze_id(id_key: str):
    manual_files = find_matching_files(id_key, [MANUAL_DIR])
    ai_files = []
    for d in AI_DIRS:
        ai_files.extend(find_matching_files(id_key, [d]))

    manual_text = '\n\n'.join(read_text(p) for p in manual_files) if manual_files else ''

    results = []
    per_id_scores = []
    for f in sorted(set(ai_files)):
        for case in parse_ai_cases(f):
            cls, score, metrics = classify_ai_vs_manual(case['text'], manual_text)
            results.append({
                'file': f,
                'class': cls,
                'score': score,
                'metrics': metrics,
            })
            per_id_scores.append(score)

    return {
        'id': id_key,
        'manual_files': manual_files,
        'ai_files': sorted(set(ai_files)),
        'manual_count': len(manual_files),
        'ai_count': len(list(results)),
        'results': results,
        'avg_score': round(sum(per_id_scores) / len(per_id_scores), 2) if per_id_scores else 0.0,
    }


def write_outputs(per_id):
    lines = []
    summary_rows = []

    lines.append('### Batch Accuracy Report')
    lines.append('')
    total_new = total_ext = total_dup = 0
    total_tests = 0

    for item in per_id:
        id_key = item['id']
        counts = Counter(r['class'] for r in item['results'])
        total_new += counts.get('NEW', 0)
        total_ext += counts.get('EXTENDS', 0)
        total_dup += counts.get('DUPLICATE', 0)
        total_tests += len(item['results'])

        lines.append(f'#### {id_key}')
        lines.append(f'- Manual files: {len(item["manual_files"])}, AI cases: {len(item["results"])}, Avg Score/30: {item["avg_score"]}')
        lines.append(f'- NEW: {counts.get("NEW",0)} | EXTENDS: {counts.get("EXTENDS",0)} | DUPLICATE: {counts.get("DUPLICATE",0)}')
        examples = item['results'][:3]
        for ex in examples:
            lines.append(f'  - {ex["class"]} {os.path.basename(ex["file"])} score={ex["score"]} ({ex["metrics"]["reason"]})')
        lines.append('')

        summary_rows.append([
            id_key,
            str(item['manual_count']),
            str(item['ai_count']),
            f'{item["avg_score"]}',
            f'{round(item["avg_score"]*100/30, 1) if item["avg_score"] else 0.0}',
            str(counts.get('NEW',0)),
            str(counts.get('EXTENDS',0)),
            str(counts.get('DUPLICATE',0)),
        ])

    # Roll-up
    lines.append('## Roll-up Summary')
    lines.append(f'- Total IDs: {len(per_id)}')
    lines.append(f'- Total AI tests: {total_tests}')
    if total_tests:
        lines.append(f'- %NEW: {round(100.0*total_new/total_tests,1)}% | %EXTENDS: {round(100.0*total_ext/total_tests,1)}% | %DUPLICATE: {round(100.0*total_dup/total_tests,1)}%')
    else:
        lines.append('- %NEW: 0.0% | %EXTENDS: 0.0% | %DUPLICATE: 0.0%')

    with open(REPORT_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'SAVED: {REPORT_MD}')

    with open(SUMMARY_CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['ID', 'ManualCount', 'AICount', 'Score/30', 'Score%', 'NEW', 'EXTENDS', 'DUPLICATE'])
        for row in summary_rows:
            w.writerow(row)
    print(f'SAVED: {SUMMARY_CSV}')


def main():
    ensure_dirs()
    ids = read_ids(IDS_FILE)
    if not ids:
        print('No IDs found in story_ids.txt')
        return
    per_id = []
    for key in ids:
        per_id.append(analyze_id(key))
    write_outputs(per_id)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'ERROR: {e}')
        sys.exit(1)



