#!/usr/bin/env python3
import os
import json


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HELP_DIR = os.path.join(BASE_DIR, 'help_center')
OUT_JSON = os.path.join(HELP_DIR, 'knowledge_index.json')


def walk_help(dir_path):
    docs = []
    for root, _dirs, files in os.walk(dir_path):
        for f in files:
            if not f.lower().endswith(('.md', '.markdown', '.txt')):
                continue
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    docs.append((path, fh.read()))
            except Exception:
                continue
    return docs


def chunk_to_qa(path, text):
    title = ''
    lines = text.splitlines()
    for ln in lines:
        if ln.strip().startswith('#') or ln.strip().startswith('###'):
            title = ln.strip('# ').strip()
            break
    bullets = [ln.strip('- ').strip() for ln in lines if ln.strip().startswith('- ')]
    return {
        'id': os.path.basename(path),
        'title': title or os.path.basename(path),
        'bullets': bullets[:20],
        'path': path,
    }


def main():
    docs = walk_help(HELP_DIR)
    qa = [chunk_to_qa(p, t) for p, t in docs]
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump({'entries': qa}, f, indent=2)
    print(f'SAVED: {OUT_JSON}')


if __name__ == '__main__':
    main()



