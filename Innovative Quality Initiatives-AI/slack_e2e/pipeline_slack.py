#!/usr/bin/env python3
import csv
import os
import re
import sys
import hashlib
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse, parse_qs
from difflib import SequenceMatcher


OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    ''
)
THREADS_DIR = os.path.join(OUTPUT_DIR, 'threads')
NORMALIZED_CSV = os.path.join(OUTPUT_DIR, 'normalized.csv')
CANDIDATES_CSV = os.path.join(OUTPUT_DIR, 'candidates.csv')
CANDIDATES_DEDUP_CSV = os.path.join(OUTPUT_DIR, 'candidates_dedup.csv')


def ensure_dirs() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(THREADS_DIR, exist_ok=True)


def find_slack_csv(start_dir: str) -> str:
    target_lower = 'e2e-issues reported through slack.csv'
    for root, _dirs, files in os.walk(start_dir):
        for f in files:
            if f.lower() == target_lower:
                return os.path.join(root, f)
    raise FileNotFoundError('Could not locate "E2E-Issues reported through Slack.csv" in repository')


def try_import_dateutil():
    try:
        from dateutil import parser as dp  # type: ignore
        return dp
    except Exception:
        return None


DATEUTIL = try_import_dateutil()


def parse_datetime(value: str):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    # Remove common timezone words for robustness
    text = re.sub(r'\bUTC\b', '', text, flags=re.IGNORECASE).strip()
    text = re.sub(r'\bGMT\b', '', text, flags=re.IGNORECASE).strip()
    if DATEUTIL:
        try:
            return DATEUTIL.parse(text)
        except Exception:
            pass
    # Try common formats
    fmts = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y/%m/%d %H:%M:%S',
        '%Y/%m/%d %H:%M',
        '%m/%d/%Y %H:%M:%S',
        '%m/%d/%Y %H:%M',
        '%m/%d/%y %H:%M:%S',
        '%m/%d/%y %H:%M',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d',
    ]
    for fmt in fmts:
        try:
            return datetime.strptime(text, fmt)
        except Exception:
            continue
    # As a last resort, try to parse epoch-like strings
    try:
        if text.isdigit():
            # seconds
            ts = int(text)
            if 1000000000 < ts < 20000000000:  # second or millisecond epoch
                if ts > 2000000000:
                    ts = ts // 1000
                return datetime.fromtimestamp(ts)
    except Exception:
        pass
    return None


def safe_str(value) -> str:
    if value is None:
        return ''
    return str(value)


def extract_thread_id(permalink: str, channel: str, text: str, fallback_key: str) -> str:
    if permalink:
        try:
            parsed = urlparse(permalink)
            q = parse_qs(parsed.query)
            # Prefer explicit thread_ts if available
            if 'thread_ts' in q and q['thread_ts']:
                ts = q['thread_ts'][0]
                # Include channel id segment from path if present
                m = re.search(r'/archives/([A-Z0-9]+)/', parsed.path)
                chan_id = m.group(1) if m else channel or 'unknown'
                return f'{chan_id}-{ts}'.replace('/', '_')
            # Otherwise look for /p<16digits>
            m = re.search(r'/p(\d{16})', parsed.path)
            if m:
                core = m.group(1)
                m2 = re.search(r'/archives/([A-Z0-9]+)/', parsed.path)
                chan_id = m2.group(1) if m2 else channel or 'unknown'
                return f'{chan_id}-{core}'
        except Exception:
            pass
    base = f"{channel}|{fallback_key}|{text[:40]}"
    digest = hashlib.md5(base.encode('utf-8')).hexdigest()[:12]
    return f'gen-{digest}'


def normalize_records(rows):
    # Map likely field names
    possible_time = ['Date/Time', 'Date', 'Time', 'Timestamp', 'Created At']
    possible_channel = ['Channel', 'channel', 'Channel Name']
    possible_permalink = ['Permalink', 'permalink', 'Link']
    possible_text = ['Text', 'Message', 'Message Text', 'Body', 'Content']
    possible_author = ['Author', 'User', 'From', 'Sender']

    records = []
    for idx, row in enumerate(rows):
        # Find columns dynamically
        time_val = None
        for k in possible_time:
            if k in row and safe_str(row[k]):
                time_val = row[k]
                break
        channel_val = None
        for k in possible_channel:
            if k in row and safe_str(row[k]):
                channel_val = row[k]
                break
        permalink_val = None
        for k in possible_permalink:
            if k in row and safe_str(row[k]):
                permalink_val = row[k]
                break
        text_val = ''
        for k in possible_text:
            if k in row and safe_str(row[k]):
                text_val = row[k]
                break
        author_val = None
        for k in possible_author:
            if k in row and safe_str(row[k]):
                author_val = row[k]
                break

        dt = parse_datetime(safe_str(time_val)) or datetime.fromtimestamp(0)
        channel = safe_str(channel_val) or 'unknown'
        permalink = safe_str(permalink_val)
        text = safe_str(text_val)
        author = safe_str(author_val)
        fallback_key = f'{idx}-{author}-{dt.isoformat()}'
        thread_id = extract_thread_id(permalink, channel, text, fallback_key)

        records.append({
            'thread_id': thread_id,
            'channel': channel,
            'dt': dt,
            'permalink': permalink,
            'text': text,
            'author': author,
        })
    return records


JIRA_RE = re.compile(r'\bIO-\d+\b', re.IGNORECASE)
PR_RE = re.compile(r'https?://github\.com/[^/\s]+/[^/\s]+/pull/\d+', re.IGNORECASE)
SEV_RE = re.compile(r'\b(P0|P1|P2)\b', re.IGNORECASE)
PROD_RE = re.compile(r'\b(prod|production)\b', re.IGNORECASE)
ACTION_RE = re.compile(r'\b(fix|hotfix|rollback|revert|patched|rca|deployed)\b', re.IGNORECASE)
REGRESSION_RE = re.compile(r'\b(regression|escape|escaped)\b', re.IGNORECASE)


def aggregate_threads(records):
    threads = defaultdict(list)
    for rec in records:
        threads[rec['thread_id']].append(rec)

    agg = []
    for tid, msgs in threads.items():
        msgs_sorted = sorted(msgs, key=lambda m: m['dt'])
        channel = msgs_sorted[0]['channel'] if msgs_sorted else 'unknown'
        first_dt = msgs_sorted[0]['dt'] if msgs_sorted else datetime.fromtimestamp(0)
        last_dt = msgs_sorted[-1]['dt'] if msgs_sorted else datetime.fromtimestamp(0)
        texts = [m['text'] for m in msgs_sorted if m['text']]
        full_text = '\n'.join(texts)

        jira_keys = sorted(set(m.upper() for m in JIRA_RE.findall(full_text)))
        pr_urls = sorted(set(PR_RE.findall(full_text)))
        sev_match = SEV_RE.findall(full_text)
        sev = ''
        if sev_match:
            # Pick highest severity present
            sev_set = set(s.upper() for s in sev_match)
            if 'P0' in sev_set:
                sev = 'P0'
            elif 'P1' in sev_set:
                sev = 'P1'
            elif 'P2' in sev_set:
                sev = 'P2'

        prod = bool(PROD_RE.search(full_text))
        action = bool(ACTION_RE.search(full_text))
        regression_flag = bool(REGRESSION_RE.search(full_text))

        # Digest: up to 8 snippets, first non-empty lines truncated
        snippets = []
        for t in texts:
            line = t.strip()
            if not line:
                continue
            snippets.append(line[:200])
            if len(snippets) >= 8:
                break
        digest = '\n'.join(f'- {s}' for s in snippets)

        agg.append({
            'thread_id': tid,
            'channel': channel,
            'first_seen_at': first_dt,
            'last_seen_at': last_dt,
            'message_count': len(msgs_sorted),
            'jira_keys': jira_keys,
            'pr_urls': pr_urls,
            'sev': sev,
            'prod': prod,
            'action': action,
            'regression_flag': regression_flag,
            'digest': digest,
            'full_text': full_text,
        })
    return agg


def write_normalized(threads):
    with open(NORMALIZED_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'thread_id', 'channel', 'first_seen_at', 'last_seen_at', 'message_count',
            'jira_keys', 'pr_urls', 'sev', 'prod', 'action', 'digest',
        ])
        for t in sorted(threads, key=lambda x: (x['last_seen_at'], x['thread_id'])):
            writer.writerow([
                t['thread_id'],
                t['channel'],
                t['first_seen_at'].isoformat(sep=' '),
                t['last_seen_at'].isoformat(sep=' '),
                t['message_count'],
                ' '.join(t['jira_keys']),
                ' '.join(t['pr_urls']),
                t['sev'],
                'true' if t['prod'] else 'false',
                'true' if t['action'] else 'false',
                t['digest'].replace('\r', ' ').replace('\n', ' \n '),
            ])

    print(f'SAVED: {NORMALIZED_CSV}')


def write_thread_markdowns(threads):
    for t in threads:
        fname = re.sub(r'[^A-Za-z0-9._-]', '_', t['thread_id']) + '.md'
        path = os.path.join(THREADS_DIR, fname)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"# Thread {t['thread_id']}\n")
            f.write(f"Channel: {t['channel']}\n\n")
            f.write(f"First seen: {t['first_seen_at'].isoformat(sep=' ')}\n\n")
            f.write(f"Last seen: {t['last_seen_at'].isoformat(sep=' ')}\n\n")
            f.write('## Digest\n')
            f.write(t['digest'] + '\n\n')
            if t['jira_keys']:
                f.write('## Jira\n')
                f.write(', '.join(t['jira_keys']) + '\n\n')
            if t['pr_urls']:
                f.write('## PRs\n')
                for u in t['pr_urls']:
                    f.write(f'- {u}\n')
                f.write('\n')


def score_thread(t, min_dt: datetime, max_dt: datetime) -> float:
    score = 0.0
    if t['prod']:
        score += 5
    if t['sev'] in ('P0', 'P1'):
        score += 4
    elif t['sev'] == 'P2':
        score += 2
    if t['action']:
        score += 3
    if t['jira_keys']:
        score += 2
    if t['pr_urls']:
        score += 1
    # Recency bonus, scaled 0..1
    recency = 0.0
    try:
        total_span = (max_dt - min_dt).total_seconds()
        if total_span > 0:
            recency = (t['last_seen_at'] - min_dt).total_seconds() / total_span
            if recency < 0:
                recency = 0.0
            if recency > 1:
                recency = 1.0
    except Exception:
        recency = 0.0
    score += recency
    return round(score, 3), recency


def select_candidates(threads):
    if not threads:
        return []
    min_dt = min(t['last_seen_at'] for t in threads)
    max_dt = max(t['last_seen_at'] for t in threads)

    candidates = []
    for t in threads:
        is_candidate = (
            t['prod'] or
            (t['sev'] in ('P0', 'P1')) or
            t['action'] or
            bool(t['jira_keys']) or
            bool(t['pr_urls']) or
            t['regression_flag']
        )
        if not is_candidate:
            continue
        score, recency = score_thread(t, min_dt, max_dt)
        entry = {
            **t,
            'score': score,
            'recency': recency,
        }
        candidates.append(entry)

    candidates.sort(key=lambda x: (x['score'], x['last_seen_at']), reverse=True)
    return candidates


def write_candidates(candidates):
    with open(CANDIDATES_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'thread_id', 'channel', 'first_seen_at', 'last_seen_at', 'message_count',
            'jira_keys', 'pr_urls', 'sev', 'prod', 'action', 'score', 'recency', 'digest',
        ])
        for c in candidates:
            writer.writerow([
                c['thread_id'],
                c['channel'],
                c['first_seen_at'].isoformat(sep=' '),
                c['last_seen_at'].isoformat(sep=' '),
                c['message_count'],
                ' '.join(c['jira_keys']),
                ' '.join(c['pr_urls']),
                c['sev'],
                'true' if c['prod'] else 'false',
                'true' if c['action'] else 'false',
                f"{c['score']:.3f}",
                f"{c['recency']:.3f}",
                c['digest'].replace('\r', ' ').replace('\n', ' \n '),
            ])
    print(f'SAVED: {CANDIDATES_CSV}')


def similarity(a: str, b: str) -> float:
    a = a or ''
    b = b or ''
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def deduplicate_candidates(candidates):
    n = len(candidates)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    # Build clusters: shared Jira OR digest sim >= 0.80
    for i in range(n):
        for j in range(i + 1, n):
            shared_jira = False
            if candidates[i]['jira_keys'] and candidates[j]['jira_keys']:
                set_i = set(k.upper() for k in candidates[i]['jira_keys'])
                set_j = set(k.upper() for k in candidates[j]['jira_keys'])
                if set_i.intersection(set_j):
                    shared_jira = True
            sim = similarity(candidates[i]['digest'], candidates[j]['digest'])
            if shared_jira or sim >= 0.80:
                union(i, j)

    clusters = defaultdict(list)
    for idx in range(n):
        clusters[find(idx)].append(idx)

    output_rows = []
    for root, indices in clusters.items():
        # Pick canonical by highest score, then latest
        indices_sorted = sorted(indices, key=lambda k: (candidates[k]['score'], candidates[k]['last_seen_at']), reverse=True)
        canonical_idx = indices_sorted[0]
        canonical = candidates[canonical_idx]
        dup_ids = [candidates[k]['thread_id'] for k in indices_sorted[1:]]
        row = {
            **canonical,
            'duplicates': ' '.join(dup_ids),
        }
        output_rows.append(row)

    # Sort canonical rows
    output_rows.sort(key=lambda x: (x['score'], x['last_seen_at']), reverse=True)
    duplicates_removed = n - len(output_rows)

    with open(CANDIDATES_DEDUP_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'thread_id', 'channel', 'first_seen_at', 'last_seen_at', 'message_count',
            'jira_keys', 'pr_urls', 'sev', 'prod', 'action', 'score', 'recency', 'duplicates', 'digest',
        ])
        for r in output_rows:
            writer.writerow([
                r['thread_id'],
                r['channel'],
                r['first_seen_at'].isoformat(sep=' '),
                r['last_seen_at'].isoformat(sep=' '),
                r['message_count'],
                ' '.join(r['jira_keys']),
                ' '.join(r['pr_urls']),
                r['sev'],
                'true' if r['prod'] else 'false',
                'true' if r['action'] else 'false',
                f"{r['score']:.3f}",
                f"{r['recency']:.3f}",
                r['duplicates'],
                r['digest'].replace('\r', ' ').replace('\n', ' \n '),
            ])

    print(f'SAVED: {CANDIDATES_DEDUP_CSV}')
    print(f'COUNTS: clusters={len(output_rows)}, duplicates_removed={duplicates_removed}')
    return output_rows, duplicates_removed, len(output_rows)


def read_csv_rows(path: str):
    rows = []
    with open(path, 'r', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    ensure_dirs()
    src_csv = find_slack_csv(repo_root)

    rows = read_csv_rows(src_csv)
    records = normalize_records(rows)
    threads = aggregate_threads(records)

    write_normalized(threads)
    write_thread_markdowns(threads)

    candidates = select_candidates(threads)
    write_candidates(candidates)
    deduplicate_candidates(candidates)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'ERROR: {e}')
        sys.exit(1)


