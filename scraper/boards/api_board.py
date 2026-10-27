"""HTTP/API job boards that return full postings without a browser listing step."""

from __future__ import annotations

import html
import json
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any, List, Optional

from core.markets import posting_accepts_us_workers, stamp_market_fields
from core.role_filters import posting_matches_role
from core.state import JobData

from .base import BaseJobParser

_USER_AGENT = (
    "Mozilla/5.0 (compatible; FlowResumeUSRemoteScraper/1.0; +https://github.com/HammadAhsan341)"
)


def _http_get(url: str, timeout: float = 45.0) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT, "Accept": "*/*"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def _plain_html(value: str) -> str:
    text = html.unescape(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


class ApiBoardParser(BaseJobParser):
    """Base for boards backed by JSON or RSS feeds."""

    enrich_from_detail_pages = False
    api_url: str = ""

    def parse_job(self, response: Any) -> Optional[JobData]:
        return None

    def parse_listing(self, response: Any) -> List[str]:
        return []

    def build_search_url(self, query: str, location: str = "", page: int = 1) -> str:
        return self.api_url

    def fetch_jobs_direct(
        self,
        query: str,
        location: str = "",
        max_jobs: Optional[int] = None,
        page_limit: int = 1,
    ) -> List[JobData]:
        raise NotImplementedError


class RemoteOkParser(ApiBoardParser):
    board_name = "remoteok"
    api_url = "https://remoteok.com/api"

    def fetch_jobs_direct(
        self,
        query: str,
        location: str = "",
        max_jobs: Optional[int] = None,
        page_limit: int = 1,
    ) -> List[JobData]:
        del page_limit
        raw = json.loads(_http_get(self.api_url).decode("utf-8", errors="replace"))
        if not isinstance(raw, list):
            return []
        jobs: List[JobData] = []
        for row in raw:
            if not isinstance(row, dict) or not row.get("id"):
                continue
            title = str(row.get("position") or row.get("title") or "").strip()
            company = str(row.get("company") or "Unknown").strip()
            if not title or not posting_matches_role(query, title, ""):
                continue
            location_text = str(row.get("location") or "Remote").strip()
            if not posting_accepts_us_workers(location_text):
                continue
            description = _plain_html(str(row.get("description") or ""))
            if len(description) < 40:
                continue
            slug = str(row.get("slug") or "").strip()
            job_url = f"https://remoteok.com/remote-jobs/{slug}" if slug else "https://remoteok.com/"
            job: JobData = {
                "job_id": self.generate_job_id(title, company, location_text or "Remote"),
                "title": title,
                "company": company or "Unknown",
                "location": location_text or "Remote, United States",
                "job_url": job_url,
                "board": self.board_name,
                "description": description,
                "skills": list(row.get("tags") or []),
                "posted_date": str(row.get("date") or "") or None,
                "salary": None,
                "employment_type": None,
                "experience_required": None,
                "raw_html": None,
            }
            jobs.append(stamp_market_fields(job, search_location=location))
            if max_jobs and len(jobs) >= max_jobs:
                break
        return jobs


class RemotiveParser(ApiBoardParser):
    board_name = "remotive"
    api_url = "https://remotive.com/api/remote-jobs"

    def fetch_jobs_direct(
        self,
        query: str,
        location: str = "",
        max_jobs: Optional[int] = None,
        page_limit: int = 1,
    ) -> List[JobData]:
        del page_limit
        payload = json.loads(_http_get(self.api_url).decode("utf-8", errors="replace"))
        rows = payload.get("jobs") if isinstance(payload, dict) else None
        if not isinstance(rows, list):
            return []
        jobs: List[JobData] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            title = str(row.get("title") or "").strip()
            company = str(row.get("company_name") or "Unknown").strip()
            if not title or not posting_matches_role(query, title, ""):
                continue
            location_text = str(row.get("candidate_required_location") or "Remote").strip()
            if not posting_accepts_us_workers(location_text):
                continue
            description = _plain_html(str(row.get("description") or ""))
            if len(description) < 40:
                continue
            job_url = str(row.get("url") or "").strip()
            if not job_url:
                continue
            job: JobData = {
                "job_id": self.generate_job_id(title, company, location_text or "Remote"),
                "title": title,
                "company": company or "Unknown",
                "location": location_text or "Remote, United States",
                "job_url": job_url,
                "board": self.board_name,
                "description": description,
                "skills": list(row.get("tags") or []),
                "posted_date": str(row.get("publication_date") or "") or None,
                "salary": str(row.get("salary") or "") or None,
                "employment_type": str(row.get("job_type") or "") or None,
                "experience_required": None,
                "raw_html": None,
            }
            jobs.append(stamp_market_fields(job, search_location=location))
            if max_jobs and len(jobs) >= max_jobs:
                break
        return jobs


_WWR_CATEGORIES = {
    "software engineer": "remote-programming-jobs",
    "developer": "remote-programming-jobs",
    "engineer": "remote-programming-jobs",
    "designer": "remote-design-jobs",
    "data": "remote-programming-jobs",
    "devops": "remote-devops-sysadmin-jobs",
    "product": "remote-product-jobs",
    "marketing": "remote-marketing-jobs",
}


class WeWorkRemotelyParser(ApiBoardParser):
    board_name = "weworkremotely"
    origin = "https://weworkremotely.com"

    def _category_slug(self, query: str) -> str:
        lowered = (query or "").lower()
        for needle, slug in _WWR_CATEGORIES.items():
            if needle in lowered:
                return slug
        return "remote-programming-jobs"

    def build_search_url(self, query: str, location: str = "", page: int = 1) -> str:
        del location, page
        slug = self._category_slug(query)
        return f"{self.origin}/categories/{slug}.rss"

    def fetch_jobs_direct(
        self,
        query: str,
        location: str = "",
        max_jobs: Optional[int] = None,
        page_limit: int = 1,
    ) -> List[JobData]:
        del page_limit
        feed_url = self.build_search_url(query)
        root = ET.fromstring(_http_get(feed_url))
        channel = root.find("channel")
        if channel is None:
            return []
        jobs: List[JobData] = []
        for item in channel.findall("item"):
            title_raw = (item.findtext("title") or "").strip()
            if not title_raw:
                continue
            if ":" in title_raw:
                company, title = [part.strip() for part in title_raw.split(":", 1)]
            else:
                company, title = "Unknown", title_raw
            if not posting_matches_role(query, title, ""):
                continue
            region = (item.findtext("{http://weworkremotely.com}region") or item.findtext("region") or "").strip()
            if not region:
                region = (item.findtext("category") or "Remote").strip()
            if not posting_accepts_us_workers(region):
                continue
            description = _plain_html(item.findtext("description") or "")
            if len(description) < 40:
                continue
            job_url = (item.findtext("link") or "").strip()
            if not job_url:
                continue
            location_text = region or "Remote, United States"
            job: JobData = {
                "job_id": self.generate_job_id(title, company, location_text),
                "title": title,
                "company": company or "Unknown",
                "location": location_text,
                "job_url": job_url,
                "board": self.board_name,
                "description": description,
                "skills": [],
                "posted_date": (item.findtext("pubDate") or "") or None,
                "salary": None,
                "employment_type": None,
                "experience_required": None,
                "raw_html": None,
            }
            jobs.append(stamp_market_fields(job, search_location=location))
            if max_jobs and len(jobs) >= max_jobs:
                break
        return jobs
