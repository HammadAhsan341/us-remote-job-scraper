"""Shared RSS/HTTP helpers for US remote feed parsers."""

from __future__ import annotations

import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from typing import List, Optional

from core.markets import posting_accepts_us_workers, stamp_market_fields
from core.role_filters import posting_matches_role
from core.state import JobData

from .base import BaseJobParser

USER_AGENT = (
    "Mozilla/5.0 (compatible; FlowResumeUSRemoteScraper/1.0; +https://github.com/HammadAhsan341)"
)


def http_get(url: str, timeout: float = 45.0) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def plain_html(value: str) -> str:
    text = html.unescape(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _item_field(item: ET.Element, *names: str) -> str:
    for name in names:
        for child in item:
            tag = child.tag.split("}")[-1]
            if tag == name and (child.text or "").strip():
                return (child.text or "").strip()
    return ""


def _item_encoded(item: ET.Element) -> str:
    for child in item:
        tag = child.tag.split("}")[-1]
        if tag in {"encoded", "content"} and (child.text or "").strip():
            return (child.text or "").strip()
    return _item_field(item, "description")


def jobs_from_rss_feed(
    parser: BaseJobParser,
    feed_url: str,
    query: str,
    location: str = "",
    max_jobs: Optional[int] = None,
    title_split: bool = True,
) -> List[JobData]:
    root = ET.fromstring(http_get(feed_url))
    channel = root.find("channel")
    if channel is None:
        return []
    jobs: List[JobData] = []
    for item in channel.findall("item"):
        title_raw = _item_field(item, "title")
        if not title_raw:
            continue
        if title_split and ":" in title_raw:
            company, title = [part.strip() for part in title_raw.split(":", 1)]
        else:
            company, title = "Unknown", title_raw
        if not posting_matches_role(query, title, ""):
            continue
        job_url = _item_field(item, "link")
        if not job_url:
            continue
        description = plain_html(_item_encoded(item))
        if len(description) < 40:
            continue
        region = plain_html(_item_field(item, "region", "creator"))
        if region and not posting_accepts_us_workers(region):
            continue
        location_text = region or location or "Remote, United States"
        job: JobData = {
            "job_id": parser.generate_job_id(title, company, location_text),
            "title": title,
            "company": company or "Unknown",
            "location": location_text,
            "job_url": job_url,
            "board": parser.board_name,
            "description": description,
            "skills": [],
            "posted_date": _item_field(item, "pubDate") or None,
            "salary": None,
            "employment_type": None,
            "experience_required": None,
            "raw_html": None,
        }
        jobs.append(stamp_market_fields(job, search_location=location))
        if max_jobs and len(jobs) >= max_jobs:
            break
    return jobs
