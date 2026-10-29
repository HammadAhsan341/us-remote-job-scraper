from datetime import datetime, timezone

from scripts.schedule_gate import should_scrape

NOW = datetime(2026, 10, 19, 10, 37, tzinfo=timezone.utc)


def test_scrapes_when_this_half_hour_has_no_success():
    runs = [{"id": 1, "conclusion": "success", "run_started_at": "2026-10-19T10:13:00Z"}]
    assert should_scrape(runs, NOW, "99")[0] is True


def test_skips_when_this_half_hour_already_succeeded():
    runs = [{"id": 2, "conclusion": "success", "run_started_at": "2026-10-19T10:33:00Z"}]
    assert should_scrape(runs, NOW, "99")[0] is False
