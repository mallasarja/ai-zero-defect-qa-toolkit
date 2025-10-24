#!/usr/bin/env python3
import os
import re
import sys
from difflib import SequenceMatcher

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)

IDS_FILE = os.path.join(BASE_DIR, 'story_ids.txt')
MANUAL_DIR = os.path.join(ROOT, 'manual_tests')
AI_DIRS = [
    os.path.join(ROOT, 'jira_stories'),
    os.path.join(ROOT, 'pr_test_cases'),
    os.path.join(ROOT, 'slack_test_cases'),
]
JIRA_INPUTS = os.path.join(ROOT, 'jira_inputs')

OUT_VERDICTS_MD = os.path.join(BASE_DIR, 'latest_final_verdicts.md')

IO_VERBS = [
    'Create Flow', 'Configure Import/Export', 'Set Mappings', 'Run Flow',
    'Check Dashboard & Logs', 'Inspect HTTP/Error payloads'
]
CAT_KEYS = {
    'A11y': ['a11y', 'accessibility', 'keyboard', 'focus', 'aria', 'contrast'],
    'Integration': ['integration', 'webhook', 'external', 'dependency'],
    'API-parity': ['api-parity', 'parity', 'config vs ui', 'api parity'],
    'Performance/Load': ['performance', 'load', 'throughput', 'latency'],
    'Security': ['security', 'rbac', 'permission', 'auth'],
    'Reliability/Recovery': ['recovery', 'restart', 'resume', 'idempotent'],
    'E2E': ['e2e', 'end-to-end', 'flow'],
    'Compatibility': ['compatibility', 'version', 'unicode'],
    'Error handling': ['error handling', 'graceful', 'retry', 'backoff', 'error'],
}


def read_text(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        return ''


def list_files(dir_path: str):
    hits = []
    if not os.path.exists(dir_path):
        return hits
    for root, _dirs, files in os.walk(dir_path):
        for f in files:
            if f.lower().endswith(('.md', '.markdown', '.txt')):
                hits.append(os.path.join(root, f))
    return hits


def find_manual_text(jira_id: str) -> str:
    texts = []
    for p in list_files(MANUAL_DIR):
        name = os.path.basename(p).lower()
        if jira_id.lower() in name or jira_id.lower() in read_text(p).lower():
            texts.append(read_text(p))
    return '\n\n'.join(texts)


def find_ai_text(jira_id: str) -> str:
    texts = []
    for d in AI_DIRS:
        for p in list_files(d):
            name = os.path.basename(p).lower()
            content = read_text(p)
            if jira_id.lower() in name or jira_id.lower() in content.lower():
                texts.append(content)
    return '\n\n'.join(texts)


def load_spec(jira_id: str) -> str:
    # Try jira_inputs/<ID>_story.md
    for ext in ['_story.md', '-story.md', '.md']:
        path = os.path.join(JIRA_INPUTS, f'{jira_id}{ext}')
        if os.path.exists(path):
            return read_text(path)
    # Fallback: jira_stories
    for p in list_files(os.path.join(ROOT, 'jira_stories')):
        if jira_id.lower() in os.path.basename(p).lower():
            return read_text(p)
    return ''


def ac_coverage(text: str) -> float:
    lines = [ln.strip() for ln in (text or '').splitlines()]
    count = sum(1 for ln in lines if ln.lower().startswith('ac-'))
    if count >= 3:
        return 100.0
    if count == 2:
        return 66.0
    if count == 1:
        return 33.0
    # Heuristic: if explicit 'Acceptance Criteria' present
    if any('acceptance criteria' in ln.lower() for ln in lines):
        return 33.0
    return 0.0


def category_coverage(text: str) -> float:
    t = (text or '').lower()
    present = 0
    for _cat, keys in CAT_KEYS.items():
        if any(k in t for k in keys):
            present += 1
    total = max(1, len(CAT_KEYS))
    return round(100.0 * present / total, 1)


def spec_completeness(text: str, spec: str) -> float:
    if not text or not spec:
        return 0.0
    r = SequenceMatcher(None, text.lower(), spec.lower()).ratio()
    return round(100.0 * r, 1)


def io_realism(text: str) -> float:
    t = (text or '').lower()
    hits = 0
    for v in IO_VERBS:
        if v.lower() in t:
            hits += 1
    return round(100.0 * hits / max(1, len(IO_VERBS)), 1)


def final_score(ac: float, cat: float, spec: float, io: float) -> float:
    return round(0.40 * ac + 0.30 * cat + 0.20 * spec + 0.10 * io, 1)


def choose_winner(ai: float, manual: float, ai_ac: float, manual_ac: float) -> str:
    diff = abs(ai - manual)
    if diff >= 2.0:
        return 'AI' if ai > manual else 'MANUAL'
    if ai_ac != manual_ac:
        return 'AI' if ai_ac > manual_ac else 'MANUAL'
    return 'TIE'


def save_artifacts(jira_id: str, ai_components: dict, manual_components: dict, winner: str, ai_score: float, manual_score: float):
    # Per-ID markdown table
    md_path = os.path.join(BASE_DIR, f'{jira_id}_ai_vs_manual.md')
    lines = []
    lines.append(f'### {jira_id}: AI vs Manual')
    lines.append('Component | Manual % | AI %')
    lines.append('---|---:|---:')
    for key in ['AC Coverage', 'Category Coverage', 'Spec Completeness', 'IO Realism']:
        lines.append(f"{key} | {manual_components[key]} | {ai_components[key]}")
    lines.append('')
    # Gap notes
    lines.append('Notes:')
    if manual_components.get('_missing_cats'):
        lines.append(f"- Manual missing categories: {', '.join(manual_components['_missing_cats'])}")
    if ai_components.get('_missing_cats'):
        lines.append(f"- AI missing categories: {', '.join(ai_components['_missing_cats'])}")
    if manual_components.get('_missing_verbs'):
        lines.append(f"- Manual missing IO verbs: {', '.join(manual_components['_missing_verbs'])}")
    if ai_components.get('_missing_verbs'):
        lines.append(f"- AI missing IO verbs: {', '.join(ai_components['_missing_verbs'])}")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'SAVED: {md_path}')

    # Verdict text
    verdict_line = f'FINAL VERDICT: {winner} — AI {ai_score}% vs Manual {manual_score}% — Jira {jira_id}'
    txt_path = os.path.join(BASE_DIR, f'{jira_id}_final_verdict.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(verdict_line + '\n')
    print(f'SAVED: {txt_path}')

    # Append to latest_final_verdicts.md
    row = f'| {jira_id} | {manual_score}% | {ai_score}% | {winner} |'
    header = '| Jira ID | Manual % | AI % | Winner |\n|---|---:|---:|---|\n'
    if not os.path.exists(OUT_VERDICTS_MD) or os.path.getsize(OUT_VERDICTS_MD) == 0:
        with open(OUT_VERDICTS_MD, 'w', encoding='utf-8') as f:
            f.write(header)
            f.write(row + '\n')
    else:
        with open(OUT_VERDICTS_MD, 'a', encoding='utf-8') as f:
            f.write(row + '\n')
    print(f'SAVED: {OUT_VERDICTS_MD}')

    return verdict_line


def evaluate(jira_id: str):
    manual_text = find_manual_text(jira_id)
    ai_text = find_ai_text(jira_id)
    spec = load_spec(jira_id)

    def build_components(text: str):
        ac = ac_coverage(text)
        cat = category_coverage(text)
        specc = spec_completeness(text, spec)
        io = io_realism(text)
        # For notes: missing categories and verbs
        t = (text or '').lower()
        missing_cats = []
        for cat_name, keys in CAT_KEYS.items():
            if not any(k in t for k in keys):
                missing_cats.append(cat_name)
        missing_verbs = [v for v in IO_VERBS if v.lower() not in t]
        return {
            'AC Coverage': ac,
            'Category Coverage': cat,
            'Spec Completeness': specc,
            'IO Realism': io,
            '_missing_cats': missing_cats,
            '_missing_verbs': missing_verbs,
        }

    manual_comp = build_components(manual_text)
    ai_comp = build_components(ai_text)

    manual_score = final_score(manual_comp['AC Coverage'], manual_comp['Category Coverage'], manual_comp['Spec Completeness'], manual_comp['IO Realism'])
    ai_score = final_score(ai_comp['AC Coverage'], ai_comp['Category Coverage'], ai_comp['Spec Completeness'], ai_comp['IO Realism'])

    winner = choose_winner(ai_score, manual_score, ai_comp['AC Coverage'], manual_comp['AC Coverage'])
    verdict_line = save_artifacts(jira_id, ai_comp, manual_comp, winner, ai_score, manual_score)
    # Print final line (must be last printed line for this ID)
    print(verdict_line)


def main():
    ids = []
    if '--id' in sys.argv:
        try:
            i = sys.argv.index('--id')
            val = sys.argv[i+1]
            ids = [val]
        except Exception:
            pass
    if not ids:
        # load from story_ids.txt
        if os.path.exists(IDS_FILE):
            with open(IDS_FILE, 'r', encoding='utf-8') as f:
                ids = [ln.strip() for ln in f if ln.strip()]
    if not ids:
        print('No IDs provided.')
        sys.exit(1)

    last_verdict = ''
    for jid in ids:
        evaluate(jid)
        # The last printed line in evaluate is the verdict; capture not necessary for printing


if __name__ == '__main__':
    main()



