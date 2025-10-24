#!/usr/bin/env python3
import csv
import os
import re
import sys
from collections import defaultdict
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEDUP_CSV = os.path.join(BASE_DIR, 'candidates_dedup.csv')
NORMALIZED_CSV = os.path.join(BASE_DIR, 'normalized.csv')
CONTEXT_DIR = os.path.join(BASE_DIR, 'context')
TEST_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'slack_test_cases')
INDEX_MD = os.path.join(TEST_ROOT, 'INDEX.md')


JIRA_RE = re.compile(r'\bIO-\d+\b', re.IGNORECASE)
PR_RE = re.compile(r'https?://github\.com/[^/\s]+/[^/\s]+/pull/\d+', re.IGNORECASE)
SEV_RE = re.compile(r'\b(P0|P1|P2)\b', re.IGNORECASE)
PROD_RE = re.compile(r'\b(prod|production)\b', re.IGNORECASE)
REGRESSION_RE = re.compile(r'\b(regression|escape|escaped)\b', re.IGNORECASE)


def ensure_dirs():
    os.makedirs(CONTEXT_DIR, exist_ok=True)
    os.makedirs(TEST_ROOT, exist_ok=True)


def read_candidates(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, 'r', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def read_normalized(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, 'r', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def to_bool(s: str) -> bool:
    return str(s).strip().lower() in ('true', '1', 'yes', 'y')


def split_multi(s: str):
    s = (s or '').strip()
    if not s:
        return []
    # Values were saved space-separated
    return [p for p in s.replace(',', ' ').split(' ') if p]


def undigest(text: str) -> str:
    # Reverse the saved digest formatting back to multi-line bullets when possible
    return (text or '').replace(' \n ', '\n')


def summarize_reason(row, digest_text: str) -> str:
    reasons = []
    if to_bool(row.get('prod', 'false')):
        reasons.append('prod')
    sev = (row.get('sev') or '').upper()
    if sev in ('P0', 'P1', 'P2'):
        reasons.append(f'sev={sev}')
    if to_bool(row.get('action', 'false')):
        reasons.append('action')
    if split_multi(row.get('jira_keys', '')):
        reasons.append('jira')
    if split_multi(row.get('pr_urls', '')):
        reasons.append('pr')
    if REGRESSION_RE.search(digest_text or ''):
        reasons.append('regression/escape')
    return ', '.join(reasons) or 'candidate'


def guess_component(digest_text: str) -> str:
    t = (digest_text or '').lower()
    if any(k in t for k in ['oauth', 'jwt', 'auth']):
        return 'auth'
    if any(k in t for k in ['import', 'export', 'flow', 'mapping', 'transform']):
        return 'data-pipeline'
    if any(k in t for k in ['dashboard', 'ui', 'screen', 'accessibility', 'keyboard', 'aria']):
        return 'ui'
    if any(k in t for k in ['webhook', 'api', 'endpoint', 'http', 'rest', 'retry', 'backoff']):
        return 'api'
    if any(k in t for k in ['scheduler', 'job', 'queue']):
        return 'scheduler'
    return 'core'


def derive_ac_from_digest(digest_text: str, has_jira: bool):
    lines = [l.strip('- ').strip() for l in (digest_text or '').splitlines() if l.strip('- ').strip()]
    bullets = []
    for ln in lines:
        # Turn a snippet into a requirement-ish statement
        # e.g., "flow failed on mapping" -> "Flow should successfully process mappings without failure"
        lower = ln.lower()
        if 'fail' in lower or 'error' in lower or 'exception' in lower:
            bullets.append('System should complete the operation without errors and provide clear failure diagnostics.')
        elif 'timeout' in lower or 'slow' in lower or 'latency' in lower:
            bullets.append('Operation should complete within acceptable latency thresholds under expected load.')
        elif 'permission' in lower or 'rbac' in lower or 'forbidden' in lower:
            bullets.append('RBAC should restrict/allow actions appropriately based on user roles.')
        elif 'mapping' in lower or 'transform' in lower:
            bullets.append('Configured mappings must be applied correctly to input/output records.')
        elif 'oauth' in lower or 'jwt' in lower:
            bullets.append('Authentication and token handling must succeed and refresh as needed.')
        elif 'dashboard' in lower or 'ui' in lower:
            bullets.append('UI should present accurate status with accessible interactions and feedback.')
        elif 'export' in lower or 'import' in lower or 'flow' in lower:
            bullets.append('Flow execution should process inputs to outputs deterministically per configuration.')
        else:
            bullets.append('Feature should function per expected configuration without regressions.')
        if len(bullets) >= 5:
            break
    if not bullets:
        bullets = [
            'Feature should function per expected configuration without regressions.',
            'Errors should be handled with actionable diagnostics and recovery hints.',
            'Operation should meet performance SLAs under expected load.',
        ]
    if has_jira:
        # If Jira exists, keep AC minimal to avoid conflicting with Jira's AC
        bullets = bullets[:3]
    else:
        bullets = bullets[:5]
    return bullets


def derive_repro_hints(digest_text: str):
    t = (digest_text or '')
    hints = []
    # Extract common clues
    tenant = re.findall(r'\btenant[:=]?\s*([A-Za-z0-9_-]+)', t, flags=re.IGNORECASE)
    flow = re.findall(r'\bflow[:#\s-]*([A-Za-z0-9_-]+)', t, flags=re.IGNORECASE)
    job = re.findall(r'\bjob[:#\s-]*([A-Za-z0-9_-]+)', t, flags=re.IGNORECASE)
    env = re.findall(r'\b(env|environment)[:=]?\s*([A-Za-z0-9_-]+)', t, flags=re.IGNORECASE)
    endpoint = re.findall(r'https?://[^\s)]+', t)
    if tenant:
        hints.append(f'Use tenant: {tenant[0]}')
    if env:
        hints.append(f'Environment: {env[0][1]}')
    if flow:
        hints.append(f'Flow: {flow[0]}')
    if job:
        hints.append(f'Job: {job[0]}')
    if endpoint:
        hints.append(f'Endpoint sample: {endpoint[0]}')
    if not hints:
        hints = [
            'Create representative flow and configuration matching Slack details.',
            'Reproduce using same data shape and schedule if mentioned.',
        ]
    return hints


def derive_risk_notes(digest_text: str):
    t = (digest_text or '').lower()
    impact = []
    if any(k in t for k in ['import', 'export', 'flow']):
        impact.append('data-pipeline correctness and data integrity')
    if any(k in t for k in ['oauth', 'jwt', 'auth']):
        impact.append('authentication/authorization flows')
    if any(k in t for k in ['dashboard', 'ui']):
        impact.append('user experience and visibility')
    if any(k in t for k in ['timeout', 'slow', 'latency', 'queue']):
        impact.append('performance and throughput')
    if any(k in t for k in ['rollback', 'revert']):
        impact.append('rollback procedures and change safety')
    if not impact:
        impact.append('core stability and reliability')
    notes = [
        f'Impact area: {", ".join(impact)}',
        'Blast radius: may affect multiple tenants/flows if systemic.',
        'Rollback: confirm safe rollback and data reconciliation steps.',
    ]
    return notes


def save_context_capsule(row, digest_text: str):
    thread_id = row.get('thread_id')
    path = os.path.join(CONTEXT_DIR, f'{thread_id}_context.md')

    channel = row.get('channel', '')
    first_seen = row.get('first_seen_at', '')
    last_seen = row.get('last_seen_at', '')
    message_count = row.get('message_count', '')
    sev = (row.get('sev') or '').upper() or 'N/A'
    prod = 'true' if to_bool(row.get('prod', 'false')) else 'false'
    jira_keys = ' '.join(split_multi(row.get('jira_keys', '')))
    pr_urls = ' '.join(split_multi(row.get('pr_urls', '')))
    reason = summarize_reason(row, digest_text)
    permalink = ''  # not available in dedup; leave blank if not present

    ac_bullets = derive_ac_from_digest(digest_text, has_jira=bool(jira_keys))
    repro_hints = derive_repro_hints(digest_text)
    risk_notes = derive_risk_notes(digest_text)

    with open(path, 'w', encoding='utf-8') as f:
        f.write('### 1) Slack Summary\n')
        f.write(f'- Channel: {channel}\n')
        f.write(f'- Window: {first_seen} → {last_seen}\n')
        f.write(f'- Message Count: {message_count}\n')
        f.write(f'- Sev/Prod: {sev}/{prod}\n')
        f.write(f'- Reason: {reason}\n')
        f.write(f'- Jira Keys: {jira_keys or "N/A"}\n')
        f.write(f'- PR URLs: {pr_urls or "N/A"}\n')
        f.write(f'- Permalink: {permalink or ""}\n')
        f.write('\n')

        f.write('### 2) Highlights\n')
        if digest_text.strip():
            f.write(digest_text.strip() + '\n\n')
        else:
            f.write('- No digest available.\n\n')

        f.write('### 3) Inferred Acceptance Criteria\n')
        for i, b in enumerate(ac_bullets, start=1):
            f.write(f'- AC-{i}: {b}\n')
        f.write('\n')

        f.write('### 4) Repro Hints\n')
        for h in repro_hints:
            f.write(f'- {h}\n')
        f.write('\n')

        f.write('### 5) Risk Notes\n')
        for r in risk_notes:
            f.write(f'- {r}\n')
        f.write('\n')

    print(f'SAVED: {path}')
    return path, len(ac_bullets)


def test_case_block(case_id: str, title: str, pre: list, steps: list, data: list, expected: list, tags: dict, test_type: str):
    lines = []
    lines.append(f'- Test Case ID: {case_id}')
    lines.append(f'- Title/Description: {title}')
    lines.append(f'- Preconditions:')
    for p in pre:
        lines.append(f'  - {p}')
    lines.append(f'- Test Steps:')
    for s in steps:
        lines.append(f'  - {s}')
    lines.append(f'- Test Data:')
    for d in data:
        lines.append(f'  - {d}')
    lines.append(f'- Expected Result:')
    for e in expected:
        lines.append(f'  - {e}')
    lines.append(f'- Actual Result:')
    lines.append(f'  - TBT')
    lines.append(f'- Status:')
    lines.append(f'  - Not Run')
    lines.append(f'- Postconditions:')
    lines.append(f'  - Cleanup temporary resources and revert configs')
    tag_str = ', '.join([f'{k}={v}' for k, v in tags.items()])
    lines.append(f'- Tags/Labels: {tag_str}')
    lines.append(f'- Test Type: {test_type}')
    return '\n'.join(lines)


def build_tests_for_thread(row, digest_text: str, ac_count: int):
    thread_id = row.get('thread_id')
    sev = (row.get('sev') or 'N/A').upper()
    prod = 'true' if to_bool(row.get('prod', 'false')) else 'false'
    jira_keys = split_multi(row.get('jira_keys', ''))
    component = guess_component(digest_text)
    tags = {
        'source': 'slack',
        'thread_id': thread_id,
        'sev': sev or 'N/A',
        'prod': prod,
        'jira': ' '.join(jira_keys) if jira_keys else 'N/A',
        'component': component,
    }

    file_path = os.path.join(TEST_ROOT, f'SLK-{thread_id}.md')

    ac_tags = [f'AC-{i}' for i in range(1, ac_count + 1)] or ['AC-1']
    header = []
    header.append(f'### Slack-derived Test Suite: SLK-{thread_id}')
    header.append('')
    header.append('#### UI')
    header.append('')

    cases = []
    case_idx = 1

    def mkid(prefix):
        nonlocal case_idx
        cid = f'{prefix}-{case_idx:03d}'
        case_idx += 1
        return cid

    # E2E scenario (UI)
    steps_ui = [
        'Create Flow',
        'Configure Import/Export',
        'Set Mappings',
        'Run Flow',
        'Check Dashboard & Logs',
        'Inspect HTTP/Error payloads',
    ]
    data_ui = [
        'Valid sample CSV/JSON per mapping',
        'Edge-case record (nulls, long strings, unicode)',
        'Invalid record (schema mismatch)',
    ]
    pre_ui = ['User has appropriate RBAC role', 'Tenant exists', 'Feature flags as per Slack context']

    # Positive
    cases.append(test_case_block(
        mkid('E2E-UI'),
        'End-to-end happy path matches Slack AC',
        pre_ui,
        steps_ui,
        data_ui[:1],
        ['Flow completes, dashboard green, outputs correct, logs clean'] + ac_tags,
        tags,
        'E2E',
    ))
    # Negative
    cases.append(test_case_block(
        mkid('E2E-UI'),
        'End-to-end with invalid inputs yields actionable errors',
        pre_ui,
        steps_ui,
        data_ui[2:3],
        ['Flow fails gracefully with clear error, no partial corruption'],
        tags,
        'Error handling',
    ))
    # Edge
    cases.append(test_case_block(
        mkid('E2E-UI'),
        'End-to-end with edge cases (nulls/length/unicode)',
        pre_ui,
        steps_ui,
        data_ui[1:2],
        ['Flow completes, edge records handled per config'],
        tags,
        'Compatibility',
    ))

    # A11y (UI)
    steps_a11y = ['Navigate UI with keyboard only', 'Verify focus order', 'Check aria roles and contrast']
    cases.append(test_case_block(
        mkid('A11Y-UI'),
        'Accessibility checks for screens involved',
        ['Screen reachable and states load correctly'],
        steps_a11y,
        [],
        ['Meets WCAG AA for keyboard, focus, roles, contrast'],
        tags,
        'A11y',
    ))

    header.append('\n\n'.join(cases))

    # Backend section
    header.append('')
    header.append('#### BE')
    header.append('')

    cases_be = []
    case_idx = 1

    # Integration
    steps_be_int = ['Create Flow', 'Configure Import/Export', 'Set Mappings', 'Run Flow', 'Validate DB/HTTP outputs']
    cases_be.append(test_case_block(
        mkid('INT-BE'),
        'Integration with external systems per config',
        ['Service healthy and credentials valid'],
        steps_be_int,
        ['External endpoint stubs or sandbox accounts'],
        ['Requests/responses match contract; retries/backoff as expected'],
        tags,
        'Integration',
    ))
    # API-parity
    cases_be.append(test_case_block(
        mkid('PAR-BE'),
        'API parity: config vs UI produce identical outputs',
        ['Have equivalent API config and UI config'],
        ['Apply config via API', 'Apply same via UI', 'Run Flow', 'Compare outputs'],
        ['Config JSON, UI steps script'],
        ['Outputs identical, no drift'],
        tags,
        'API-parity',
    ))
    # Performance/Load
    cases_be.append(test_case_block(
        mkid('PERF-BE'),
        'Performance: sustained load meets SLA',
        ['Service scaled to expected size'],
        ['Run Flow with N batch size for M minutes'],
        ['N, M from Slack or defaults (e.g., N=1000, M=15)'],
        ['Latency and throughput within SLA; no errors'],
        tags,
        'Performance/Load',
    ))
    # Security (RBAC)
    cases_be.append(test_case_block(
        mkid('SEC-BE'),
        'RBAC: operations restricted to authorized roles',
        ['Create roles: admin, operator, viewer'],
        ['Attempt create/run as each role'],
        [],
        ['Only authorized roles succeed; others receive 403/meaningful error'],
        tags,
        'Security',
    ))
    # Reliability/Recovery
    cases_be.append(test_case_block(
        mkid('REL-BE'),
        'Recovery from service restart and resume',
        ['Have long-running flow'],
        ['Start flow', 'Restart service mid-run', 'Resume processing'],
        [],
        ['No duplication or loss; idempotent behavior'],
        tags,
        'Reliability/Recovery',
    ))
    # Error handling (backend)
    cases_be.append(test_case_block(
        mkid('ERR-BE'),
        'Error handling with bad external responses',
        ['Stub 4xx/5xx from dependency'],
        ['Run flow and observe retries/backoff'],
        [],
        ['Graceful failure with retries, circuit breaker if configured'],
        tags,
        'Error handling',
    ))

    header.append('\n\n'.join(cases_be))

    content = '\n'.join(header) + '\n'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'SAVED: {file_path}')

    # Count test types
    test_type_counts = defaultdict(int)
    for tt in ['E2E', 'Error handling', 'Compatibility', 'A11y', 'Integration', 'API-parity', 'Performance/Load', 'Security', 'Reliability/Recovery']:
        test_type_counts[tt] += content.count(f'- Test Type: {tt}')

    total_tests = content.count('- Test Case ID: ')
    return file_path, total_tests, test_type_counts


def write_index(summary_rows):
    lines = []
    lines.append('### Slack Test Cases Index')
    lines.append('')
    for r in summary_rows:
        lines.append(f'- {r["thread_id"]} → {r["file"]} | sev={r["sev"]} prod={r["prod"]} jira={r["jira"]} | tests={r["tests"]}')
    lines.append('')
    with open(INDEX_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'SAVED: {INDEX_MD}')


def main():
    ensure_dirs()
    rows = read_candidates(DEDUP_CSV)

    summary_rows = []
    total_type_counts = defaultdict(int)

    # Fallback: if no candidates, pick top-N from normalized by recency
    FALLBACK_TOP_N = 20
    if not rows:
        norm = read_normalized(NORMALIZED_CSV)
        # sort by last_seen_at desc
        def parse_dt(s):
            try:
                return datetime.fromisoformat((s or '').strip())
            except Exception:
                return datetime.min
        norm_sorted = sorted(norm, key=lambda r: parse_dt(r.get('last_seen_at', '')), reverse=True)
        rows = []
        for r in norm_sorted[:FALLBACK_TOP_N]:
            rows.append({
                'thread_id': r.get('thread_id', ''),
                'channel': r.get('channel', ''),
                'first_seen_at': r.get('first_seen_at', ''),
                'last_seen_at': r.get('last_seen_at', ''),
                'message_count': r.get('message_count', ''),
                'jira_keys': r.get('jira_keys', ''),
                'pr_urls': r.get('pr_urls', ''),
                'sev': r.get('sev', ''),
                'prod': r.get('prod', ''),
                'action': r.get('action', ''),
                'digest': r.get('digest', ''),
            })

    for row in rows:
        thread_id = row.get('thread_id')
        digest_text = undigest(row.get('digest', ''))

        # A) Context capsule
        _capsule_path, ac_count = save_context_capsule(row, digest_text)

        # B) Test suites
        file_path, num_tests, type_counts = build_tests_for_thread(row, digest_text, ac_count)

        for k, v in type_counts.items():
            total_type_counts[k] += v

        summary_rows.append({
            'thread_id': thread_id,
            'file': os.path.basename(file_path),
            'sev': (row.get('sev') or 'N/A').upper(),
            'prod': 'true' if to_bool(row.get('prod', 'false')) else 'false',
            'jira': ' '.join(split_multi(row.get('jira_keys', ''))) or 'N/A',
            'tests': num_tests,
        })

    write_index(summary_rows)

    # Summary by Test Type
    if summary_rows:
        print('SUMMARY: Test Type counts:')
        for k in sorted(total_type_counts.keys()):
            print(f'- {k}: {total_type_counts[k]}')
    else:
        print('SUMMARY: No candidates to generate tests for.')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'ERROR: {e}')
        sys.exit(1)


