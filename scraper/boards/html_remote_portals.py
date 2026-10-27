"""Browser-backed US remote boards (PublicBoardParser subclasses)."""

from __future__ import annotations

import re
import urllib.parse

from .public import PublicBoardParser


class DiceParser(PublicBoardParser):
    board_name = "dice"
    origin = "https://www.dice.com"
    listing_selectors = ("div[data-testid='job-search-serp-card']", "article", "div.card")
    title_selectors = ("a[data-testid='job-search-job-detail-link']", "h5 a", "h2 a")
    company_selectors = ("a[data-testid='job-search-job-company']", ".company", "span.company")
    location_selectors = ("[data-testid='job-search-job-location']", ".location")
    job_href_pattern = re.compile(r"/job-detail/", re.I)

    def build_search_url(self, query: str, location: str = "", page: int = 1) -> str:
        params = {"q": query or "software engineer", "location": location or "Remote"}
        if page > 1:
            params["page"] = str(page)
        return f"{self.origin}/jobs?{urllib.parse.urlencode(params)}"


class BuiltinParser(PublicBoardParser):
    board_name = "builtin"
    origin = "https://builtin.com"
    listing_selectors = ("div[data-id='job-card']", "article", "div.job-card")
    title_selectors = ("h2 a", "h3 a", "[data-id='job-title'] a")
    company_selectors = ("[data-id='company-title']", ".company")
    location_selectors = ("[data-id='job-location']", ".location")
    job_href_pattern = re.compile(r"/job/", re.I)

    def build_search_url(self, query: str, location: str = "", page: int = 1) -> str:
        params = {"search": query or "software engineer"}
        if page > 1:
            params["page"] = str(page)
        return f"{self.origin}/jobs/remote?{urllib.parse.urlencode(params)}"


class RemoteCoParser(PublicBoardParser):
    board_name = "remote_co"
    origin = "https://remote.co"
    listing_selectors = ("article.job_listing", "div.job-listing", "li.job")
    title_selectors = ("h2 a", "h3 a", ".position a")
    company_selectors = (".company", ".company-name")
    location_selectors = (".location", ".region")
    job_href_pattern = re.compile(r"/remote-jobs/", re.I)

    def build_search_url(self, query: str, location: str = "", page: int = 1) -> str:
        params = {"search_keywords": query or "software engineer"}
        if page > 1:
            params["paged"] = str(page)
        return f"{self.origin}/remote-jobs/search?{urllib.parse.urlencode(params)}"


class DynamiteJobsParser(PublicBoardParser):
    board_name = "dynamitejobs"
    origin = "https://dynamitejobs.com"
    listing_selectors = ("div.job-card", "article", "li.job")
    title_selectors = ("h2 a", "h3 a", ".job-title a")
    company_selectors = (".company-name", ".company")
    location_selectors = (".location",)
    job_href_pattern = re.compile(r"/remote-jobs/", re.I)

    def build_search_url(self, query: str, location: str = "", page: int = 1) -> str:
        params = {"search": query or "software engineer"}
        if page > 1:
            params["page"] = str(page)
        return f"{self.origin}/remote-jobs?{urllib.parse.urlencode(params)}"


class JustRemoteParser(PublicBoardParser):
    board_name = "justremote"
    origin = "https://justremote.co"
    listing_selectors = ("div.job-card", "article", "li")
    title_selectors = ("h2 a", "h3 a", ".job-title")
    company_selectors = (".company",)
    location_selectors = (".location",)
    job_href_pattern = re.compile(r"/remote-", re.I)

    def build_search_url(self, query: str, location: str = "", page: int = 1) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", (query or "software developer").lower()).strip("-")
        return f"{self.origin}/remote-{slug}-jobs"


class ArcParser(PublicBoardParser):
    board_name = "arc"
    origin = "https://arc.dev"
    listing_selectors = ("article", "div.job-card", "li")
    title_selectors = ("h2 a", "h3 a")
    company_selectors = (".company",)
    location_selectors = (".location",)
    job_href_pattern = re.compile(r"/remote-jobs/", re.I)

    def build_search_url(self, query: str, location: str = "", page: int = 1) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", (query or "software-engineer").lower()).strip("-")
        path = slug.replace("-", "-")
        if page > 1:
            return f"{self.origin}/remote-jobs/{path}?page={page}"
        return f"{self.origin}/remote-jobs/{path}"


class ZipRecruiterParser(PublicBoardParser):
    board_name = "ziprecruiter"
    origin = "https://www.ziprecruiter.com"
    listing_selectors = ("article", "div.job_result", "li")
    title_selectors = ("h2 a", "a.job_link")
    company_selectors = (".company",)
    location_selectors = (".location",)
    job_href_pattern = re.compile(r"/jobs/", re.I)

    def build_search_url(self, query: str, location: str = "", page: int = 1) -> str:
        params = {"search": query or "software engineer", "location": "Remote"}
        if page > 1:
            params["page"] = str(page)
        return f"{self.origin}/jobs-search?{urllib.parse.urlencode(params)}"


class MonsterParser(PublicBoardParser):
    board_name = "monster"
    origin = "https://www.monster.com"
    listing_selectors = ("section.card-content", "article", "div.job-card")
    title_selectors = ("h2 a", "h3 a")
    company_selectors = (".company",)
    location_selectors = (".location",)
    job_href_pattern = re.compile(r"/job-openings/", re.I)

    def build_search_url(self, query: str, location: str = "", page: int = 1) -> str:
        q = urllib.parse.quote(query or "software engineer")
        return f"{self.origin}/jobs/search?q={q}&where=Remote&page={page}"


class CareerBuilderParser(PublicBoardParser):
    board_name = "careerbuilder"
    origin = "https://www.careerbuilder.com"
    listing_selectors = ("div.data-results-content", "article", "li")
    title_selectors = ("h2 a", "a.data-results-content")
    company_selectors = (".company",)
    location_selectors = (".location",)
    job_href_pattern = re.compile(r"/job/", re.I)

    def build_search_url(self, query: str, location: str = "", page: int = 1) -> str:
        params = {
            "keywords": query or "software engineer",
            "location": "Remote",
            "page_number": str(page),
        }
        return f"{self.origin}/jobs?{urllib.parse.urlencode(params)}"


class WellfoundParser(PublicBoardParser):
    board_name = "wellfound"
    origin = "https://wellfound.com"
    listing_selectors = ("div[data-test='JobSearchResult']", "article", "div.job")
    title_selectors = ("h2 a", "a.job_link")
    company_selectors = (".company",)
    location_selectors = (".location",)
    job_href_pattern = re.compile(r"/jobs/", re.I)

    def build_search_url(self, query: str, location: str = "", page: int = 1) -> str:
        slug = urllib.parse.quote((query or "software engineer").lower())
        return f"{self.origin}/role/l/remote/{slug}?page={page}"
