# GitHub Actions setup

The scraper **does not run** until this repo has the same Action secrets as `job-scraper` / `gulf-job-scraper`.

## Required secrets

| Secret | Purpose |
| :----- | :------ |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (scraper only) |
| `PERMITTED_ROLES_1` | JSON array of roles (set 1) |
| `PERMITTED_ROLES_2` | JSON array of roles (set 2) |

## Recommended (optional)

| Secret | Purpose |
| :----- | :------ |
| `JOB_SCRAPING_MAX_PAGES_PER_BOARD` | Listing depth |
| `JOB_SCRAPING_DOWNLOAD_DELAY` | Throttle between fetches |
| `JOB_SCRAPING_RETRY_BACKOFF_SECONDS` | Failed-role retry wait |
| `JOB_STALE_AFTER_DAYS` | Stale cleanup window |
| `JOBS_CACHE_REFRESH_URL` | FlowResume API cache refresh |
| `JOBS_CRON_SECRET` | Cache refresh auth |

## Manual run

**Actions → US Remote Job Scrape → Run workflow**

- **Boards:** `all` (default)
- **Country:** `US`
- **Role set:** `all` or `1` / `2`

Scheduled runs use cron `13,33,53 * * * *` (UTC).

## Copy secrets from another repo

From a machine that has `job-scraper/.env` with the values:

```bash
./scripts/sync_github_secrets_from_env.sh /path/to/job-scraper/.env
```
