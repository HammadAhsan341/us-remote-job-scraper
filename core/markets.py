"""US remote market metadata and location normalization."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Market:
    code: str
    country: str
    currency: str
    indeed_host: str
    aliases: tuple[str, ...]
    market: str = "us_remote"

    @property
    def linkedin_location(self) -> str:
        return self.country


@dataclass(frozen=True)
class ResolvedLocation:
    market: str
    country_code: str
    country: str
    city: str
    state_or_emirate: str
    currency: str
    indeed_host: str
    location_label: str
    remote: bool = True

    @property
    def query_location(self) -> str:
        return self.location_label


US_MARKET = Market(
    code="US",
    country="United States",
    currency="USD",
    indeed_host="www.indeed.com",
    aliases=("us", "usa", "u s a", "united states", "america"),
)

US_COUNTRY_CODES: tuple[str, ...] = (US_MARKET.code,)


def _norm_key(value: str) -> str:
    text = (value or "").lower().replace("&", " and ")
    text = text.replace(".", "")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


_COUNTRY_ALIAS: Dict[str, Market] = {}
for _alias in (US_MARKET.code, US_MARKET.country, *US_MARKET.aliases):
    _COUNTRY_ALIAS[_norm_key(_alias)] = US_MARKET


def market_by_code(code: str) -> Optional[Market]:
    token = (code or "").strip().upper()
    if token == US_MARKET.code:
        return US_MARKET
    return None


def search_location_labels(
    country_codes: Iterable[str] | None = None,
    include_cities: bool = True,
) -> List[str]:
    """Remote US is a single search shard; cities are not used."""
    del include_cities
    del country_codes
    return ["Remote, United States"]


def remote_location_label(country_code: str = "US") -> str:
    del country_code
    return "Remote, United States"


def resolve_location(text: str) -> Optional[ResolvedLocation]:
    raw = " ".join((text or "").replace("·", ",").split())
    if not raw:
        return None

    remote = True
    body = raw
    if not body.lower().startswith("remote"):
        if _lookup_country(body):
            remote = "remote" in _norm_key(body)
        body = re.sub(r"^remote\b[\s,:\-]*", "", body, count=1, flags=re.IGNORECASE).strip(" ,")

    market = _lookup_country(body) or _lookup_country(raw) or US_MARKET
    return ResolvedLocation(
        market=market.market,
        country_code=market.code,
        country=market.country,
        city="",
        state_or_emirate="",
        currency=market.currency,
        indeed_host=market.indeed_host,
        location_label="Remote, United States",
        remote=remote,
    )


def _lookup_country(text: str) -> Optional[Market]:
    return _COUNTRY_ALIAS.get(_norm_key(text))


def source_host_from_url(url: str) -> str:
    host = (urlsplit(url or "").hostname or "").lower().removeprefix("www.")
    if host.endswith("linkedin.com"):
        return "linkedin.com"
    return host


def default_currency(location: str = "", country_code: str = "") -> str:
    if market_by_code(country_code):
        return US_MARKET.currency
    resolved = resolve_location(location)
    if resolved and resolved.currency:
        return resolved.currency
    return "USD"


_CURRENCY_RULES: tuple[tuple[str, str], ...] = (
    (r"(?:\$|\busd\b|\bus\$\b)", "USD"),
    (r"(?:£|\bgbp\b)", "GBP"),
    (r"(?:€|\beur\b)", "EUR"),
    (r"(?:\bpkr\b|\brs\.?(?!\w)|\brupees?\b)", "PKR"),
)


def currency_in_text(salary: str) -> str:
    """Explicit currency token in a salary string, or empty when there is none."""
    text = salary or ""
    for pattern, code in _CURRENCY_RULES:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return code
    return ""


_US_HIRE_PATTERN = re.compile(
    r"\b("
    r"united states|u\.?\s*s\.?\s*a\.?|usa|us only|us-based|"
    r"north america|anywhere in the world|worldwide|global|"
    r"remote|no location|"
    r"americas|western hemisphere"
    r")\b",
    re.IGNORECASE,
)


def posting_accepts_us_workers(location_text: str) -> bool:
    """Heuristic for API/RSS location strings on remote-first boards."""
    text = (location_text or "").strip()
    if not text:
        return True
    if _US_HIRE_PATTERN.search(text):
        return True
    # Explicit non-US only regions we can skip quickly.
    blocked = ("eu only", "europe only", "uk only", "canada only", "australia only")
    lowered = text.lower()
    return not any(token in lowered for token in blocked)


def stamp_market_fields(job: Dict, search_location: str = "") -> Dict:
    out = dict(job)
    chosen = resolve_location(str(out.get("location") or search_location or "")) or resolve_location(
        "Remote, United States"
    )
    if chosen:
        out["market"] = chosen.market
        out["country_code"] = chosen.country_code
        out["country"] = chosen.country
        if not out.get("location"):
            out["location"] = chosen.location_label
    host = source_host_from_url(str(out.get("job_url") or out.get("url") or ""))
    if host:
        out["source_host"] = host
    return out

