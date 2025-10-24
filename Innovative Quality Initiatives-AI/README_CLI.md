### Celigo Quality CLI

Usage:

```bash
python3 Innovative\ Quality\ Initiatives-AI/cli.py fetch-jira --days 90 --statuses "Ready for QA,QA Validation,EPIC Testing,Integration Testing,Done"
python3 Innovative\ Quality\ Initiatives-AI/cli.py fetch-prs --label "Ready for QA" --days 90
python3 Innovative\ Quality\ Initiatives-AI/cli.py gen-jira --id IO-141368
python3 Innovative\ Quality\ Initiatives-AI/cli.py gen-jira --all
python3 Innovative\ Quality\ Initiatives-AI/cli.py gen-pr --pr 14192
python3 Innovative\ Quality\ Initiatives-AI/cli.py gen-pr --latest 10
python3 Innovative\ Quality\ Initiatives-AI/cli.py gen-slack --csv "E2E-Issues reported through Slack.csv"
python3 Innovative\ Quality\ Initiatives-AI/cli.py compare --id IO-141368 --manual Innovative\ Quality\ Initiatives-AI/manual_tests/
python3 Innovative\ Quality\ Initiatives-AI/cli.py batch-accuracy --ids Innovative\ Quality\ Initiatives-AI/validation/story_ids.txt
python3 Innovative\ Quality\ Initiatives-AI/cli.py backlog
python3 Innovative\ Quality\ Initiatives-AI/cli.py dashboard
```

Each command prints a `Done:` line with exit status on completion.
