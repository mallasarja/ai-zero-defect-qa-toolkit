## IO Stories JIRA export

Run the script to export IO Stories created in the last 90 days with status Ready for QA or Done. Output CSV is saved in this folder.

### Prereqs
- Python 3.9+
- `pip install requests`
- Env vars set:
  - `JIRA_BASE_URL` (e.g., https://your-domain.atlassian.net)
  - `JIRA_EMAIL`
  - `JIRA_API_TOKEN`

### Usage
```bash
export JIRA_BASE_URL="https://your-domain.atlassian.net"
export JIRA_EMAIL="you@example.com"
export JIRA_API_TOKEN="<token>"

python3 fetch_jira_io_stories.py
```

Override JQL or output path if needed:
```bash
python3 fetch_jira_io_stories.py \
  --jql 'project = IO AND issuetype = Story AND status in ("Ready for QA", Done) AND created >= -90d ORDER BY updated DESC' \
  --output "Innovative Quality Initiatives-AI/io_stories_custom.csv"
```

