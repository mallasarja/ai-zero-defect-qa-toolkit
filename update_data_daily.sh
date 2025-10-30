#!/bin/sh
set -euo pipefail

# Resolve repo root in CI or local
PROJECT_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")"/.. && pwd)}"
PUBLIC_DIR="$PROJECT_ROOT/zero-defect-dashboard/public"
LOG_FILE="$PUBLIC_DIR/update_last_run.log"

TIMESTAMP() { date "+%Y-%m-%d %H:%M:%S"; }

{
  echo "[\"$(TIMESTAMP)\"] Starting Zero-Defect data refresh"

  # Activate venv if available
  if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    . "$PROJECT_ROOT/.venv/bin/activate"
  fi

  export PYTHONUNBUFFERED=1
  export GITHUB_INCLUDE_COMMITS=0

  cd "$PROJECT_ROOT"

  echo "[\"$(TIMESTAMP)\"] Fetching Jira bugs..."
  python3 fetch_mcp_bugs.py || true

  echo "[\"$(TIMESTAMP)\"] Fetching GitHub PR matches (last 2y)..."
  python3 fetch_github_prs_last_2y.py || true

  echo "[\"$(TIMESTAMP)\"] Joining bugs with PRs..."
  python3 join_bugs_with_prs.py || true

  echo "[\"$(TIMESTAMP)\"] Generating KPIs..."
  python3 zero-defect-dashboard/generate_kpis_from_join.py || true

  if [ -f "$PROJECT_ROOT/zero-defect-dashboard/generate_ai_testing_impact.py" ]; then
    echo "[\"$(TIMESTAMP)\"] Generating AI testing impact..."
    python3 zero-defect-dashboard/generate_ai_testing_impact.py || true
  fi

  if [ -f "$PROJECT_ROOT/zero-defect-dashboard/generate_automation_coverage.py" ]; then
    echo "[\"$(TIMESTAMP)\"] Generating automation coverage & escaped without tests..."
    python3 zero-defect-dashboard/generate_automation_coverage.py || true
  fi

  if [ -f "$PROJECT_ROOT/zero-defect-dashboard/generate_customer_impact.py" ]; then
    echo "[\"$(TIMESTAMP)\"] Generating customer impact..."
    python3 zero-defect-dashboard/generate_customer_impact.py || true
  fi

  if [ -f "$PROJECT_ROOT/zero-defect-dashboard/generate_bug_trend_releasewise.py" ]; then
    echo "[\"$(TIMESTAMP)\"] Generating release-wise trend breakdown..."
    python3 zero-defect-dashboard/generate_bug_trend_releasewise.py || true
  fi

  echo "[\"$(TIMESTAMP)\"] Refresh complete"
} >> "$LOG_FILE" 2>&1

