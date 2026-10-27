"""Additional US remote job portals (API/RSS feeds)."""

from __future__ import annotations

import json
import re
import urllib.parse
from typing import Any, List, Optional

from core.markets import posting_accepts_us_workers, stamp_market_fields
from core.role_filters import posting_matches_role
from core.state import JobData

from .api_board import ApiBoardParser
from .feed_utils import http_get, jobs_from_rss_feed, plain_html


def _append_job(
    parser: ApiBoardParser,
    jobs: List[JobData],
    *,
    title: str,
    company: str,
    description: str,
    job_url: str,
    location: str,
    query: str,
    max_jobs: Optional[int],
    posted_date: Optional[str] = None,
    salary: Optional[str] = None,
    employment_type: Optional[str] = None,
    skills: Optional[list] = None,
) -> bool:
    if not title or not posting_matches_role(query, title, job_url):
        return False
    if not posting_accepts_us_workers(location):
        return False
    if len(plain_html(description)) < 40 and len((description or "").strip()) < 40:
        return False
    desc = plain_html(description) if "<" in (description or "") else (description or "").strip()
    if len(desc) < 40:
        return False
    job: JobData = {
        "job_id": parser.generate_job_id(title, company or "Unknown", location or "Remote"),
        "title": title,
        "company": company or "Unknown",
        "location": location or "Remote, United States",
        "job_url": job_url,
        "board": parser.board_name,
        "description": desc,
        "skills": skills or [],
        "posted_date": posted_date,
        "salary": salary,
        "employment_type": employment_type,
        "experience_required": None,
        "raw_html": None,
    }
    jobs.append(stamp_market_fields(job, search_location=location))
    return max_jobs is not None and len(jobs) >= max_jobs


class HimalayasParser(ApiBoardParser):
    board_name = "himalayas"
    api_url = "https://himalayas.app/jobs/api"

    def fetch_jobs_direct(
        self,
        query: str,
        location: str = "",
        max_jobs: Optional[int] = None,
        page_limit: int = 1,
    ) -> List[JobData]:
        del page_limit
        jobs: List[JobData] = []
        cursor: Optional[str] = None
        pages = 0
        while pages < 8:
            pages += 1
            params = {"limit": "50"}
            if cursor:
                params["cursor"] = cursor
            url = f"{self.api_url}?{urllib.parse.urlencode(params)}"
            payload = json.loads(http_get(url).decode("utf-8", errors="replace"))
            rows = payload.get("jobs") if isinstance(payload, dict) else None
            if not isinstance(rows, list) or not rows:
                break
            for row in rows:
                if not isinstance(row, dict):
                    continue
                title = str(row.get("title") or "").strip()
                company = str(row.get("companyName") or "Unknown").strip()
                loc = str(row.get("locationRestrictions") or row.get("timezoneRestrictions") or "Remote")
                desc = str(row.get("description") or row.get("excerpt") or "")
                link = str(row.get("applicationLink") or "").strip()
                if not link:
                    slug = str(row.get("companySlug") or "")
                    guid = str(row.get("guid") or "")
                    if slug and guid:
                        link = f"https://himalayas.app/companies/{slug}/jobs/{guid}"
                if _append_job(
                    self,
                    jobs,
                    title=title,
                    company=company,
                    description=desc,
                    job_url=link or "https://himalayas.app/jobs",
                    location=loc,
                    query=query,
                    max_jobs=max_jobs,
                    posted_date=str(row.get("pubDate") or "") or None,
                    salary=_salary(row),
                    employment_type=str(row.get("employmentType") or "") or None,
                ):
                    return jobs
            cursor = payload.get("nextCursor") if isinstance(payload, dict) else None
            if not cursor:
                break
        return jobs


def _salary(row: dict) -> Optional[str]:
    parts = []
    currency = row.get("currency")
    low = row.get("minSalary")
    high = row.get("maxSalary")
    period = row.get("salaryPeriod")
    if currency and (low or high):
        parts.append(str(currency))
    if low and high:
        parts.append(f"{low}-{high}")
    elif low:
        parts.append(str(low))
    if period:
        parts.append(f"per {period}")
    return " ".join(parts) if parts else None


class WorkingNomadsParser(ApiBoardParser):
    board_name = "workingnomads"
    api_url = "https://www.workingnomads.com/api/exposed_jobs/"

    def fetch_jobs_direct(
        self,
        query: str,
        location: str = "",
        max_jobs: Optional[int] = None,
        page_limit: int = 1,
    ) -> List[JobData]:
        del page_limit
        rows = json.loads(http_get(self.api_url).decode("utf-8", errors="replace"))
        if not isinstance(rows, list):
            return []
        jobs: List[JobData] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            title = str(row.get("title") or "").strip()
            company = str(row.get("company_name") or "Unknown").strip()
            loc = str(row.get("location") or "Remote")
            if _append_job(
                self,
                jobs,
                title=title,
                company=company,
                description=str(row.get("description") or ""),
                job_url=str(row.get("url") or "").strip(),
                location=loc,
                query=query,
                max_jobs=max_jobs,
                posted_date=str(row.get("pub_date") or "") or None,
                skills=list(row.get("tags") or []),
            ):
                return jobs
        return jobs


class JobicyParser(ApiBoardParser):
    board_name = "jobicy"
    api_url = "https://jobicy.com/api/v2/remote-jobs"

    def fetch_jobs_direct(
        self,
        query: str,
        location: str = "",
        max_jobs: Optional[int] = None,
        page_limit: int = 1,
    ) -> List[JobData]:
        del page_limit
        jobs: List[JobData] = []
        cursor: Optional[str] = None
        for _ in range(6):
            params = {"count": "50", "geo": "usa"}
            if cursor:
                params["cursor"] = cursor
            url = f"{self.api_url}?{urllib.parse.urlencode(params)}"
            payload = json.loads(http_get(url).decode("utf-8", errors="replace"))
            rows = payload.get("jobs") if isinstance(payload, dict) else None
            if not isinstance(rows, list) or not rows:
                break
            for row in rows:
                if not isinstance(row, dict):
                    continue
                title = str(row.get("jobTitle") or "").strip()
                company = str(row.get("companyName") or "Unknown").strip()
                loc = str(row.get("jobGeo") or "USA")
                if _append_job(
                    self,
                    jobs,
                    title=title,
                    company=company,
                    description=str(row.get("jobDescription") or row.get("jobExcerpt") or ""),
                    job_url=str(row.get("url") or "").strip(),
                    location=loc,
                    query=query,
                    max_jobs=max_jobs,
                    posted_date=str(row.get("pubDate") or "") or None,
                    employment_type=str(row.get("jobType") or "") or None,
                ):
                    return jobs
            if not payload.get("hasMore"):
                break
            cursor = payload.get("nextCursor")
            if not cursor:
                break
        return jobs


class JobspressoParser(ApiBoardParser):
    board_name = "jobspresso"
    feed_url = "https://jobspresso.co/jobs/feed/"

    def fetch_jobs_direct(
        self,
        query: str,
        location: str = "",
        max_jobs: Optional[int] = None,
        page_limit: int = 1,
    ) -> List[JobData]:
        del page_limit
        return jobs_from_rss_feed(
            self,
            self.feed_url,
            query,
            location=location,
            max_jobs=max_jobs,
            title_split=False,
        )


class ArbeitnowParser(ApiBoardParser):
    """Remote-friendly feed (global listings; US-eligible roles kept)."""

    board_name = "arbeitnow"
    api_url = "https://www.arbeitnow.com/api/job-board-api"

    def fetch_jobs_direct(
        self,
        query: str,
        location: str = "",
        max_jobs: Optional[int] = None,
        page_limit: int = 1,
    ) -> List[JobData]:
        del page_limit
        payload = json.loads(http_get(self.api_url).decode("utf-8", errors="replace"))
        rows = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(rows, list):
            return []
        jobs: List[JobData] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            if not row.get("remote"):
                continue
            title = str(row.get("title") or "").strip()
            company = str(row.get("company_name") or "Unknown").strip()
            loc = str(row.get("location") or "Remote")
            link = str(row.get("url") or "").strip()
            if not link:
                slug = str(row.get("slug") or "").strip()
                link = f"https://www.arbeitnow.com/jobs/{slug}" if slug else ""
            if _append_job(
                self,
                jobs,
                title=title,
                company=company,
                description=str(row.get("description") or ""),
                job_url=link,
                location=loc,
                query=query,
                max_jobs=max_jobs,
            ):
                return jobs
        return jobs
