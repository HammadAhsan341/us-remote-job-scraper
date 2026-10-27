<div align="center">

# US Remote Job Scraper

**Multi-board scraper for remote roles hiring in the United States**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![Scrapling](https://img.shields.io/badge/Scrapling-0.4.7-FF6B35)](https://github.com/D4Vinci/Scrapling)
[![Supabase](https://img.shields.io/badge/Supabase-2.30-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com)

Scrape high-volume US remote hiring portals, enrich each posting, deduplicate in Supabase, and upsert with `market = us_remote` so Pakistan/Gulf catalogs stay isolated.

</div>

---

## Boards

**19 sources** — API/RSS feeds first, then browser scrapers, then Indeed/LinkedIn (US remote).

Full list: **[docs/PLATFORMS.md](docs/PLATFORMS.md)**.

---

## Quick start

```bash
cd us-remote-job-scraper
uv sync
uv run playwright install
cp .env.example .env   # Supabase + PERMITTED_ROLES
uv run python main.py
```

Apply `supabase/migrations/001_full_job_payload.sql` and `002_us_remote_market.sql` on your Supabase project before the first run.

---

## Key environment variables

| Variable                 | Default            | Purpose                 |
| :----------------------- | :----------------- | :---------------------- |
| `JOB_SCRAPING_MARKET`    | `us_remote`        | Stale-job cleanup scope |
| `JOB_SCRAPING_COUNTRIES` | `US`               | Metadata / Indeed host  |
| `JOB_SCRAPING_BOARDS`    | `all`              | See default list above  |
| `PERMITTED_ROLES`        | see `.env.example` | Role allowlist          |

---

## Related repos

| Repo                                                                   | Region   |
| :--------------------------------------------------------------------- | :------- |
| [job-scraper](https://github.com/HammadAhsan341/job-scraper)           | Pakistan |
| [gulf-job-scraper](https://github.com/HammadAhsan341/gulf-job-scraper) | GCC      |
