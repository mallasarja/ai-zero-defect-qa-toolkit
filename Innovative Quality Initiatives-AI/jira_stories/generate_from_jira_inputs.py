#!/usr/bin/env python3
import os
import glob
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)
INPUT_DIR = os.path.join(ROOT, 'jira_inputs')
OUT_DIR = BASE_DIR
PREAMBLE = os.path.join(ROOT, 'prompts', 'preamble_io_style.md')
HELP_INDEX = os.path.join(ROOT, 'reference', 'help_center', 'knowledge_index.json')


def load(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ''


def load_knowledge():
    preamble = load(PREAMBLE)
    kb = {}
    try:
        with open(HELP_INDEX, 'r', encoding='utf-8') as f:
            kb = json.load(f)
    except Exception:
        kb = {}
    return preamble, kb


def write_tests(jira_id: str, content: str, out_path: str, preamble: str, kb: dict):
    lines = []
    lines.append(f"### Jira-derived Test Suite: {jira_id}")
    if preamble:
        lines.append('')
        lines.append('#### IO Preamble')
        lines.append('')
        lines.append(preamble.strip())
    if kb.get('entries'):
        lines.append('')
        lines.append('#### Knowledge Pack (titles)')
        lines.append('')
        for e in (kb.get('entries') or [])[:10]:
            t = e.get('title')
            if t:
                lines.append(f'- {t}')
    lines.append('')
    lines.append('#### UI')
    lines.append('- Test Case ID: J-UI-001')
    lines.append('- Title/Description: Functional positive path')
    lines.append('- Preconditions:')
    lines.append('  - Tenant exists; role has access')
    lines.append('- Test Steps:')
    lines.append('  - Create Flow')
    lines.append('  - Configure Import/Export')
    lines.append('  - Set Mappings')
    lines.append('  - Run Flow')
    lines.append('  - Check Dashboard & Logs')
    lines.append('  - Inspect HTTP/Error payloads')
    lines.append('- Test Data:')
    lines.append('  - Valid sample records')
    lines.append('- Expected Result:')
    lines.append('  - Operation succeeds without errors')
    lines.append('- Actual Result:')
    lines.append('  - TBT')
    lines.append('- Status:')
    lines.append('  - Not Run')
    lines.append('- Postconditions:')
    lines.append('  - Cleanup')
    lines.append('- Tags/Labels: source=jira')
    lines.append('- Test Type: Functional')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    preamble, kb = load_knowledge()
    for path in glob.glob(os.path.join(INPUT_DIR, '*.md')):
        jira_id = os.path.basename(path).split('_')[0]
        out_path = os.path.join(OUT_DIR, f'{jira_id}-testcases_v5.md')
        write_tests(jira_id, load(path), out_path, preamble, kb)
        print(f'SAVED: {out_path}')


if __name__ == '__main__':
    main()



