#!/usr/bin/env bash
# Push scraper secrets to GitHub Actions from a local .env (values never printed).
set -euo pipefail

REPO="${GITHUB_REPO:-HammadAhsan341/us-remote-job-scraper}"
ENV_FILE="${1:?usage: sync_github_secrets_from_env.sh /path/to/.env}"

if ! command -v gh >/dev/null; then
  echo "gh CLI is required" >&2
  exit 1
fi

KEYS=(
  SUPABASE_URL
  SUPABASE_SERVICE_ROLE_KEY
  PERMITTED_ROLES_1
  PERMITTED_ROLES_2
  JOB_SCRAPING_MAX_PAGES_PER_BOARD
  JOB_SCRAPING_DOWNLOAD_DELAY
  JOB_SCRAPING_RETRY_BACKOFF_SECONDS
  JOB_STALE_AFTER_DAYS
  JOBS_CACHE_REFRESH_URL
  JOBS_CRON_SECRET
)

for key in "${KEYS[@]}"; do
  line="$(grep -E "^${key}=" "$ENV_FILE" | tail -1 || true)"
  if [[ -z "$line" ]]; then
    continue
  fi
  value="${line#*=}"
  value="${value%\"}"
  value="${value#\"}"
  printf '%s' "$value" | gh secret set "$key" --repo "$REPO"
  echo "Set $key on $REPO"
done

echo "Done. Verify: gh secret list --repo $REPO"
