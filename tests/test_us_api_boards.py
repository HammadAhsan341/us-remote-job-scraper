import unittest
from unittest.mock import patch

from scraper.boards.api_board import RemoteOkParser, RemotiveParser, WeWorkRemotelyParser


class TestUsApiBoards(unittest.TestCase):
    def test_remoteok_filters_by_role(self):
        payload = [
            {"legal": "notice"},
            {
                "id": "1",
                "slug": "acme-remote-engineer",
                "position": "Senior Software Engineer",
                "company": "Acme",
                "location": "USA",
                "description": "<p>Build APIs with Python and PostgreSQL for our US team.</p>",
                "tags": ["python"],
                "date": "2026-01-01",
            },
            {
                "id": "2",
                "slug": "other-nurse",
                "position": "Registered Nurse",
                "company": "Clinic",
                "location": "USA",
                "description": "<p>Patient care role in a hospital setting every day.</p>",
            },
        ]
        with patch("scraper.boards.api_board._http_get", return_value=__import__("json").dumps(payload).encode()):
            jobs = RemoteOkParser().fetch_jobs_direct("Software Engineer", max_jobs=5)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["board"], "remoteok")
        self.assertEqual(jobs[0]["market"], "us_remote")

    def test_remotive_returns_us_friendly_jobs(self):
        payload = {
            "jobs": [
                {
                    "id": 9,
                    "url": "https://remotive.com/remote-jobs/software-dev-123",
                    "title": "Backend Developer",
                    "company_name": "Remote Co",
                    "candidate_required_location": "USA",
                    "description": "<p>Ship backend services with Go and Kubernetes daily.</p>",
                    "tags": ["go"],
                    "publication_date": "2026-01-02",
                    "job_type": "full_time",
                    "salary": "$120k",
                }
            ]
        }
        with patch("scraper.boards.api_board._http_get", return_value=__import__("json").dumps(payload).encode()):
            jobs = RemotiveParser().fetch_jobs_direct("Backend Developer", max_jobs=3)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["country_code"], "US")

    def test_weworkremotely_parses_rss(self):
        rss = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<item>
<title>Acme: Software Engineer</title>
<link>https://weworkremotely.com/remote-jobs/acme-software-engineer</link>
<region>Anywhere in the World</region>
<description>&lt;p&gt;Write TypeScript services for a distributed US product team.&lt;/p&gt;</description>
</item>
</channel></rss>"""
        with patch("scraper.boards.api_board._http_get", return_value=rss):
            jobs = WeWorkRemotelyParser().fetch_jobs_direct("Software Engineer", max_jobs=3)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["board"], "weworkremotely")


if __name__ == "__main__":
    unittest.main()
