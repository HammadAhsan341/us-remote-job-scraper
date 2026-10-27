# GitHub Actions setup

The scraper **does not run** until this repo has the same Action secrets as `job-scraper` / `gulf-job-scraper`.

## Required secrets

| Secret                      | Purpose                         |
| :-------------------------- | :------------------------------ |
| `SUPABASE_URL`              | Supabase project URL            |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (scraper only) |
| `PERMITTED_ROLES_1`         | JSON array of roles (set 1)     |
| `PERMITTED_ROLES_2`         | JSON array of roles (set 2)     |

## Recommended (optional)

| Secret                               | Purpose                                                                                            |
| :----------------------------------- | :------------------------------------------------------------------------------------------------- |
| `JOB_SCRAPING_MAX_PAGES_PER_BOARD`   | Listing depth                                                                                      |
| `JOB_SCRAPING_DOWNLOAD_DELAY`        | Throttle between fetches                                                                           |
| `JOB_SCRAPING_RETRY_BACKOFF_SECONDS` | Failed-role retry wait                                                                             |
| `JOB_STALE_AFTER_DAYS`               | Stale cleanup window                                                                               |
| `JOBS_CACHE_REFRESH_URL`             | **Required for FlowResume Jobs UI** — e.g. `https://<api-host>/api/v1/internal/jobs-cache/refresh` |
| `JOBS_CRON_SECRET`                   | Same value as FlowResume `JOBS_CRON_SECRET` (header `X-Cron-Secret`)                               |

Without `JOBS_CACHE_REFRESH_URL`, US remote rows still land in Supabase but the Jobs browse cache (Redis) may stay on Pakistan/Gulf-only data until the API’s own refresh loop runs.

## Manual run

**Actions → US Remote Job Scrape → Run workflow**

- **Boards:** `all` (default)
- **Country:** `US`
- **Role set:** `all` or `1` / `2`

## Schedule (automatic)

| UTC   | PKT (UTC+5) | Behavior                                |
| :---- | :---------- | :-------------------------------------- |
| `:13` | `:18`       | First attempt this hour                 |
| `:33` | `:38`       | Retry if the hour has not succeeded yet |
| `:53` | `:58`       | Last attempt before the next hour       |

Board list and role set come from `scripts/schedule_slot.py`:

| Cadence                | Boards                                                                                                                                                    |
| :--------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Every UTC hour**     | All RSS/API feeds (Remote OK, Remotive, We Work Remotely, Himalayas, Working Nomads, Jobicy, Jobspresso, Arbeitnow) — role set alternates 1 / 2 each hour |
| **Even UTC hours**     | Above + browser portals (Dice, Built In, Remote.co, …)                                                                                                    |
| **Every 4th UTC hour** | Above + Indeed & LinkedIn (US remote)                                                                                                                     |

The gate in `scripts/schedule_gate.py` skips duplicate work after a **successful** run in the same UTC hour (the `:33` and `:53` crons are retries only).

Ensure **Settings → Actions → General → Workflow permissions** allow read access and that Actions are enabled for the repository.

## Copy secrets from another repo

From a machine that has `job-scraper/.env` with the values:

```bash
./scripts/sync_github_secrets_from_env.sh /path/to/job-scraper/.env
```
