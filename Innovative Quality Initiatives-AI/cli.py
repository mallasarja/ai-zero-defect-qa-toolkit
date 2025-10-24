#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))


def run(cmd: list[str]) -> int:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    sys.stdout.write(proc.stdout)
    return proc.returncode


def cmd_fetch_jira(args) -> None:
    statuses = args.statuses or 'Ready for QA,QA Validation,EPIC Testing,Integration Testing,Done'
    days = int(args.days or 90)
    quoted = [('"' + s.strip() + '"') for s in statuses.split(',') if s.strip()]
    jql = f'project = IO AND issuetype = Story AND status in ({", ".join(quoted)}) AND created >= -{days}d ORDER BY updated DESC'
    script = os.path.join(os.path.dirname(ROOT), 'fetch_jira_io_stories.py')
    code = run(['python3', script, '--jql', jql, '--output', os.path.join(ROOT, 'io_stories_last_90d.csv')])
    print(f'Done: fetch-jira (exit={code})')


def cmd_fetch_prs(args) -> None:
    label = args.label or 'Ready for QA'
    days = int(args.days or 90)
    script = os.path.join(ROOT, 'list_ready_prs.py')
    # list_ready_prs scans last 90d based on date cutoff; label used implicitly via Jira key match
    code = run(['python3', script])
    print(f'Done: fetch-prs (exit={code})')


def cmd_gen_jira(args) -> None:
    script = os.path.join(ROOT, 'jira_stories', 'generate_from_jira_inputs.py')
    if args.id and args.id.lower() != 'all':
        # generate only one by copying to temp input folder is complex; generate all and inform
        code = run(['python3', script])
    else:
        code = run(['python3', script])
    print(f'Done: gen-jira (exit={code})')


def cmd_gen_pr(args) -> None:
    if args.pr:
        script = os.path.join(ROOT, 'generate_test_cases_for_pr.py')
        code = run(['python3', script, str(args.pr)])
    else:
        script = os.path.join(ROOT, 'generate_test_cases_for_all_prs.py')
        code = run(['python3', script])
    print(f'Done: gen-pr (exit={code})')


def cmd_gen_slack(args) -> None:
    # Run pipeline to normalize, candidates, dedup, and generate tests
    pipe = os.path.join(ROOT, 'slack_e2e', 'pipeline_slack.py')
    code1 = run(['python3', pipe])
    gen = os.path.join(ROOT, 'slack_e2e', 'generate_from_candidates.py')
    code2 = run(['python3', gen])
    print(f'Done: gen-slack (exit={max(code1, code2)})')


def cmd_compare(args) -> None:
    # Use batch_accuracy single-ID by writing a temp ids file
    ids_path = os.path.join(ROOT, 'validation', 'story_ids.txt')
    # Ensure id is present (append if absent)
    try:
        with open(ids_path, 'a+', encoding='utf-8') as f:
            f.seek(0)
            content = f.read()
            if args.id not in content:
                f.write(args.id + '\n')
    except Exception:
        pass
    script = os.path.join(ROOT, 'validation', 'batch_accuracy.py')
    code = run(['python3', script])
    print(f'Done: compare (exit={code})')


def cmd_batch_accuracy(args) -> None:
    script = os.path.join(ROOT, 'validation', 'batch_accuracy.py')
    code = run(['python3', script])
    print(f'Done: batch-accuracy (exit={code})')


def cmd_backlog(args) -> None:
    script = os.path.join(ROOT, 'automation', 'build_backlog.py')
    code = run(['python3', script])
    print(f'Done: backlog (exit={code})')


def cmd_dashboard(args) -> None:
    # Rebuild Slack KPIs, then dashboards
    slack = os.path.join(ROOT, 'slack_e2e', 'crosscheck_and_kpis.py')
    _ = run(['python3', slack])
    script = os.path.join(ROOT, 'dashboard', 'build_dashboard.py')
    code = run(['python3', script])
    print(f'Done: dashboard (exit={code})')


def build_parser():
    p = argparse.ArgumentParser(description='Celigo Quality CLI')
    sub = p.add_subparsers(dest='cmd', required=True)

    pj = sub.add_parser('fetch-jira')
    pj.add_argument('--days', type=int, default=90)
    pj.add_argument('--statuses', type=str, default='Ready for QA,QA Validation,EPIC Testing,Integration Testing,Done')
    pj.set_defaults(func=cmd_fetch_jira)

    pp = sub.add_parser('fetch-prs')
    pp.add_argument('--label', type=str, default='Ready for QA')
    pp.add_argument('--days', type=int, default=90)
    pp.set_defaults(func=cmd_fetch_prs)

    gj = sub.add_parser('gen-jira')
    gj.add_argument('--id', type=str, default='--all')
    gj.add_argument('--all', action='store_true')
    gj.set_defaults(func=cmd_gen_jira)

    gp = sub.add_parser('gen-pr')
    gpa = gp.add_argument_group('gen-pr options')
    gpa.add_argument('--pr', type=int, help='PR number')
    gpa.add_argument('--latest', type=int, help='Generate latest N from CSV')
    gp.set_defaults(func=cmd_gen_pr)

    gs = sub.add_parser('gen-slack')
    gs.add_argument('--csv', type=str, default='E2E-Issues reported through Slack.csv')
    gs.set_defaults(func=cmd_gen_slack)

    cmp = sub.add_parser('compare')
    cmp.add_argument('--id', type=str, required=True)
    cmp.add_argument('--manual', type=str, default=os.path.join(ROOT, 'manual_tests'))
    cmp.set_defaults(func=cmd_compare)

    ba = sub.add_parser('batch-accuracy')
    ba.add_argument('--ids', type=str, default=os.path.join(ROOT, 'validation', 'story_ids.txt'))
    ba.set_defaults(func=cmd_batch_accuracy)

    bl = sub.add_parser('backlog')
    bl.set_defaults(func=cmd_backlog)

    db = sub.add_parser('dashboard')
    db.set_defaults(func=cmd_dashboard)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
