#!/usr/bin/env python3
import os
import re
import csv
import sys
from collections import defaultdict, Counter
from difflib import SequenceMatcher


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SLACK_DIR = os.path.join(os.path.dirname(BASE_DIR), 'slack_test_cases')
JIRA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'jira_stories')
PR_DIR = os.path.join(os.path.dirname(BASE_DIR), 'pr_test_cases')

DEDUP_REPORT = os.path.join(SLACK_DIR, 'DEDUP_REPORT.md')

AUTOMATION_DIR = os.path.join(os.path.dirname(BASE_DIR), 'automation')
AUTOMATION_BACKLOG = os.path.join(AUTOMATION_DIR, 'automation_backlog.csv')

DASHBOARD_DIR = os.path.join(os.path.dirname(BASE_DIR), 'dashboard')
QUALITY_DASHBOARD = os.path.join(DASHBOARD_DIR, 'quality_dashboard.md')
LEADERSHIP_ONEPAGER = os.path.join(DASHBOARD_DIR, 'leadership_onepager.md')


def ensure_dirs():
    os.makedirs(SLACK_DIR, exist_ok=True)
    os.makedirs(AUTOMATION_DIR, exist_ok=True)
    os.makedirs(DASHBOARD_DIR, exist_ok=True)


def read_text_files(directory, allowed_exts=(".md", ".markdown", ".txt", ".json")):
    docs = []
    if not os.path.exists(directory):
        return docs
    for root, _dirs, files in os.walk(directory):
        for f in files:
            if not f.lower().endswith(allowed_exts):
                continue
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                    docs.append((path, fh.read()))
            except Exception:
                continue
    return docs


def parse_slack_tests():
    tests = []
    for fname in sorted(os.listdir(SLACK_DIR)):
        if not fname.startswith('SLK-') or not fname.endswith('.md'):
            continue
        path = os.path.join(SLACK_DIR, fname)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            continue

        current_section = ''
        current = None
        lines = content.splitlines()
        for line in lines:
            if line.strip().startswith('#### '):
                sec = line.strip().lstrip('#').strip()
                current_section = sec
                continue
            if line.strip().startswith('- Test Case ID:'):
                if current:
                    tests.append(current)
                tcid = line.split(':', 1)[1].strip()
                current = {
                    'file': fname,
                    'path': path,
                    'section': current_section,  # UI or BE
                    'id': tcid,
                    'title': '',
                    'steps': [],
                    'test_type': '',
                    'tags': {},
                    'raw': '',
                }
            elif current and line.strip().startswith('- Title/Description:'):
                current['title'] = line.split(':', 1)[1].strip()
            elif current and line.strip() == '- Test Steps:':
                current['in_steps'] = True
            elif current and line.strip().startswith('- Test Steps:'):
                current['in_steps'] = True
            elif current and line.strip().startswith('- Test Data:'):
                current['in_steps'] = False
            elif current and line.strip().startswith('- Expected Result:'):
                current['in_steps'] = False
            elif current and line.strip().startswith('- Tags/Labels:'):
                tag_str = line.split(':', 1)[1].strip()
                tags = {}
                for kv in tag_str.split(','):
                    if '=' in kv:
                        k, v = kv.strip().split('=', 1)
                        tags[k.strip()] = v.strip()
                current['tags'] = tags
            elif current and line.strip().startswith('- Test Type:'):
                current['test_type'] = line.split(':', 1)[1].strip()
            elif current:
                # Collect steps
                if current.get('in_steps') and line.strip().startswith('- '):
                    current['steps'].append(line.strip('- ').strip())
            # Always collect raw for similarity
            if current is not None:
                current['raw'] += line + '\n'
        if current:
            tests.append(current)
    return tests


JIRA_RE = re.compile(r'\bIO-\d+\b', re.IGNORECASE)


def similarity(a: str, b: str) -> float:
    a = (a or '').strip().lower()
    b = (b or '').strip().lower()
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def build_doc_index(docs):
    index = []
    for path, text in docs:
        keys = set(k.upper() for k in JIRA_RE.findall(text))
        title = ''
        first_line = text.splitlines()[0] if text.splitlines() else ''
        title = first_line.strip('# ').strip()
        index.append({
            'path': path,
            'title': title,
            'text': text,
            'jira_keys': keys,
        })
    return index


def classify_tests(slack_tests, jira_index, pr_index):
    results = []
    examples = {'NEW': [], 'EXTENDS': [], 'DUPLICATE': []}
    counts = Counter()

    for t in slack_tests:
        tags = t.get('tags', {})
        slack_jira = set(k.upper() for k in JIRA_RE.findall(tags.get('jira', '') or ''))
        base_text = ' '.join([
            t.get('title', ''),
            ' '.join(t.get('steps', [])),
            t.get('test_type', ''),
        ])

        best = None
        best_score = 0.0
        best_src = ''
        matched_by_key = False

        # Check Jira index
        for d in jira_index:
            key_intersection = slack_jira.intersection(d['jira_keys'])
            if key_intersection:
                matched_by_key = True
                score = 1.0
            else:
                score = max(
                    similarity(base_text, d['title']),
                    similarity(base_text, d['text']),
                )
            if score > best_score:
                best_score = score
                best = d
                best_src = 'JIRA'

        # Check PR index
        for d in pr_index:
            key_intersection = slack_jira.intersection(d['jira_keys'])
            if key_intersection:
                matched_by_key = True
                score = 1.0
            else:
                score = max(
                    similarity(base_text, d['title']),
                    similarity(base_text, d['text']),
                )
            if score > best_score:
                best_score = score
                best = d
                best_src = 'PR'

        # Classification
        if matched_by_key or best_score >= 0.90:
            classification = 'DUPLICATE'
            reason = 'same Jira key' if matched_by_key else f'high similarity {best_score:.2f}'
        elif best_score >= 0.80:
            # Check if Slack adds value: negative/edge/perf/a11y
            tt = (t.get('test_type', '') or '').lower()
            adds_value = any(k in tt for k in ['a11y', 'performance', 'load', 'security', 'recovery', 'error', 'compatibility'])
            classification = 'EXTENDS' if adds_value else 'DUPLICATE'
            reason = 'extends coverage' if classification == 'EXTENDS' else f'similarity {best_score:.2f}'
        else:
            classification = 'NEW'
            reason = 'no close match'

        counts[classification] += 1
        if len(examples[classification]) < 5:
            examples[classification].append({
                'slack_id': t['id'],
                'slack_file': t['file'],
                'match_src': best_src,
                'match_path': best['path'] if best else '',
                'score': best_score,
                'reason': reason,
            })

        results.append({
            'slack': t,
            'class': classification,
            'best_match': best,
            'best_score': best_score,
            'matched_by_key': matched_by_key,
        })

    return results, counts, examples


def write_dedup_report(results, counts, examples):
    lines = []
    total = sum(counts.values()) or 1
    lines.append('### Slack vs Jira/PR Cross-Check Report')
    lines.append('')
    lines.append(f'- Total Slack tests: {total}')
    lines.append(f'- NEW: {counts.get("NEW", 0)}')
    lines.append(f'- EXTENDS: {counts.get("EXTENDS", 0)}')
    lines.append(f'- DUPLICATE: {counts.get("DUPLICATE", 0)}')
    lines.append('')
    for cls in ['NEW', 'EXTENDS', 'DUPLICATE']:
        lines.append(f'### {cls} Examples')
        for ex in examples[cls]:
            lines.append(f'- {ex["slack_id"]} in {ex["slack_file"]} → {ex["match_src"]}:{os.path.basename(ex["match_path"]) if ex["match_path"] else "(none)"} (score={ex["score"]:.2f}) [{ex["reason"]}]')
        if not examples[cls]:
            lines.append('- (none)')
        lines.append('')

    lines.append('### Gaps closed (ZPL alignment)')
    lines.append('- Regression/Escape and prod incidents surfaced via Slack threads')
    lines.append('- A11y coverage added (keyboard, focus order, aria, contrast)')
    lines.append('- API-parity between config and UI validated')
    lines.append('- Performance/Load and Reliability/Recovery scenarios emphasized')
    lines.append('')

    with open(DEDUP_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'SAVED: {DEDUP_REPORT}')


def compute_kpis(results):
    threads = set()
    tests_total = 0
    class_counts = Counter()
    sev_counts = Counter()
    prod_true = 0
    components = Counter()
    layer_counts = Counter()

    for r in results:
        t = r['slack']
        tags = t.get('tags', {})
        threads.add(tags.get('thread_id', ''))
        tests_total += 1
        class_counts[r['class']] += 1
        sev = (tags.get('sev') or 'N/A').upper()
        sev_counts[sev] += 1
        if (tags.get('prod') or '').lower() == 'true':
            prod_true += 1
        comp = tags.get('component', 'core')
        components[comp] += 1
        # Layer inference
        sec = (t.get('section') or '').lower()
        tt = (t.get('test_type') or '').lower()
        layer = 'BE'
        if 'ui' in sec or 'a11y' in tt:
            layer = 'UI'
        if 'api' in tt or 'integration' in tt:
            layer = 'API'
        if 'performance' in tt or 'load' in tt:
            layer = 'Perf'
        layer_counts[layer] += 1

    threads_processed = len([x for x in threads if x])
    kpis = {
        'threads_processed': threads_processed,
        'tests_generated': tests_total,
        'pct_new': round(100.0 * class_counts['NEW'] / tests_total, 1) if tests_total else 0.0,
        'pct_extends': round(100.0 * class_counts['EXTENDS'] / tests_total, 1) if tests_total else 0.0,
        'pct_duplicate': round(100.0 * class_counts['DUPLICATE'] / tests_total, 1) if tests_total else 0.0,
        'sev_counts': sev_counts,
        'pct_prod_true': round(100.0 * prod_true / tests_total, 1) if tests_total else 0.0,
        'top_components': components.most_common(5),
        'layer_counts': layer_counts,
        'class_counts': class_counts,
    }
    return kpis


def priority_for_test(t):
    tags = t.get('tags', {})
    sev = (tags.get('sev') or 'N/A').upper()
    prod = (tags.get('prod') or '').lower() == 'true'
    tt = (t.get('test_type') or '').lower()

    sev_w = {'P0': 4, 'P1': 3, 'P2': 2}.get(sev, 1)
    prod_w = 2 if prod else 0
    type_w = 0
    if 'performance' in tt or 'load' in tt:
        type_w = 2
    elif 'security' in tt:
        type_w = 2
    elif 'integration' in tt or 'api' in tt:
        type_w = 2
    elif 'recovery' in tt:
        type_w = 2
    else:
        type_w = 1
    score = sev_w + prod_w + type_w
    if score >= 6:
        label = f'High ({score})'
    elif score >= 4:
        label = f'Medium ({score})'
    else:
        label = f'Low ({score})'
    return label


def priority_score_for_test(t):
    tags = t.get('tags', {})
    sev = (tags.get('sev') or 'N/A').upper()
    prod = (tags.get('prod') or '').lower() == 'true'
    tt = (t.get('test_type') or '').lower()
    sev_w = {'P0': 4, 'P1': 3, 'P2': 2}.get(sev, 1)
    prod_w = 2 if prod else 0
    type_w = 0
    if 'performance' in tt or 'load' in tt:
        type_w = 2
    elif 'security' in tt:
        type_w = 2
    elif 'integration' in tt or 'api' in tt:
        type_w = 2
    elif 'recovery' in tt:
        type_w = 2
    else:
        type_w = 1
    return sev_w + prod_w + type_w


def layer_for_test(t):
    sec = (t.get('section') or '').lower()
    tt = (t.get('test_type') or '').lower()
    if 'ui' in sec or 'a11y' in tt:
        return 'UI'
    if 'api' in tt or 'integration' in tt:
        return 'API'
    if 'performance' in tt or 'load' in tt:
        return 'Perf'
    return 'BE'


def estimation_for_test(t):
    tt = (t.get('test_type') or '').lower()
    if 'performance' in tt or 'load' in tt or 'integration' in tt or 'security' in tt or 'recovery' in tt:
        return 'M'
    if 'e2e' in tt:
        return 'M'
    if 'a11y' in tt:
        return 'S'
    return 'S'


def write_backlog(results):
    headers = ['Source', 'Test Case ID', 'File', 'Priority', 'Layer', 'Estimation', 'Owner']
    with open(AUTOMATION_BACKLOG, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(headers)
        for r in results:
            t = r['slack']
            w.writerow([
                'Slack',
                t.get('id', ''),
                t.get('file', ''),
                priority_for_test(t),
                layer_for_test(t),
                estimation_for_test(t),
                '',
            ])
    print(f'SAVED: {AUTOMATION_BACKLOG}')


def write_dashboard(kpis, results):
    lines = []
    lines.append('### Slack-derived regressions')
    lines.append('')
    lines.append(f'- Threads processed: {kpis["threads_processed"]}')
    lines.append(f'- Tests generated: {kpis["tests_generated"]}')
    lines.append(f'- NEW: {kpis["class_counts"].get("NEW", 0)} ({kpis["pct_new"]}%)')
    lines.append(f'- EXTENDS: {kpis["class_counts"].get("EXTENDS", 0)} ({kpis["pct_extends"]}%)')
    lines.append(f'- DUPLICATE: {kpis["class_counts"].get("DUPLICATE", 0)} ({kpis["pct_duplicate"]}%)')
    lines.append(f'- Sev mix: ' + ', '.join([f'{k}:{v}' for k, v in kpis['sev_counts'].items()]))
    lines.append(f'- % prod=true: {kpis["pct_prod_true"]}%')
    top5 = kpis['top_components'][:5]
    lines.append(f'- Top components: ' + ', '.join([f'{k}({v})' for k, v in top5]))
    lines.append('')
    # Top 10 automation candidates (NEW/EXTENDS by priority)
    cand = [r for r in results if r['class'] in ('NEW', 'EXTENDS')]
    cand_sorted = sorted(cand, key=lambda r: (priority_score_for_test(r['slack']), r['class'] == 'NEW'), reverse=True)[:10]
    lines.append('Top 10 automation candidates:')
    for r in cand_sorted:
        t = r['slack']
        file_rel = t.get('file', '')
        tcid = t.get('id', '')
        prio = priority_for_test(t)
        lines.append(f'- [{tcid}](`Innovative Quality Initiatives-AI/slack_test_cases/{file_rel}`) {r["class"]} — {prio}')
    lines.append('')
    with open(QUALITY_DASHBOARD, 'a', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'SAVED: {QUALITY_DASHBOARD}')


def write_onepager(kpis):
    lines = []
    lines.append('### Slack-derived quality insights (one-pager)')
    lines.append('')
    lines.append(f'- Slack surfaced {kpis["class_counts"].get("NEW", 0)} NEW and {kpis["class_counts"].get("EXTENDS", 0)} EXTENDS test candidates across {kpis["threads_processed"]} threads.')
    lines.append(f'- Focus areas: ' + ', '.join([f'{k}({v})' for k, v in kpis['top_components']]))
    lines.append(f'- Immediate automation candidates prioritize prod incidents and P0/P1 scenarios (NEW+EXTENDS: {kpis["class_counts"].get("NEW", 0)+kpis["class_counts"].get("EXTENDS", 0)})')
    with open(LEADERSHIP_ONEPAGER, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'SAVED: {LEADERSHIP_ONEPAGER}')


def print_kpi_table(kpis):
    # Compact KPI table
    print('KPI TABLE:')
    print('metric,value')
    print(f'threads_processed,{kpis["threads_processed"]}')
    print(f'tests_generated,{kpis["tests_generated"]}')
    print(f'pct_new,{kpis["pct_new"]}%')
    print(f'pct_extends,{kpis["pct_extends"]}%')
    print(f'pct_duplicate,{kpis["pct_duplicate"]}%')
    print(f'pct_prod_true,{kpis["pct_prod_true"]}%')
    sev_str = ';'.join([f'{k}:{v}' for k, v in kpis['sev_counts'].items()])
    print(f'sev_mix,{sev_str}')
    comp_str = ';'.join([f'{k}:{v}' for k, v in kpis['top_components']])
    print(f'top_components,{comp_str}')


def main():
    ensure_dirs()
    slack_tests = parse_slack_tests()
    jira_docs = read_text_files(JIRA_DIR)
    pr_docs = read_text_files(PR_DIR)
    jira_index = build_doc_index(jira_docs)
    pr_index = build_doc_index(pr_docs)

    results, counts, examples = classify_tests(slack_tests, jira_index, pr_index)
    write_dedup_report(results, counts, examples)

    kpis = compute_kpis(results)
    write_backlog(results)
    write_dashboard(kpis, results)
    write_onepager(kpis)
    print_kpi_table(kpis)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'ERROR: {e}')
        sys.exit(1)


