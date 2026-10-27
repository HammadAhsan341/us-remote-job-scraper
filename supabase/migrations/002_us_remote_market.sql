-- US remote market columns. Existing Pakistan/Gulf rows stay untouched; this
-- scraper writes market = 'us_remote'. Apply after 001_full_job_payload.sql.

alter table if exists public.jobs
    add column if not exists market text not null default 'pk',
    add column if not exists country_code text,
    add column if not exists country text,
    add column if not exists city text,
    add column if not exists state_or_emirate text,
    add column if not exists source_host text;

create index if not exists jobs_market_date_scrapped_idx
    on public.jobs (market, date_scrapped desc nulls last);

create index if not exists jobs_market_country_code_idx
    on public.jobs (market, country_code);
