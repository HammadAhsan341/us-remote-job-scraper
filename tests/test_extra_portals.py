import unittest
from unittest.mock import patch

from scraper.boards.extra_remote_portals import HimalayasParser, JobspressoParser, WorkingNomadsParser


class TestExtraPortals(unittest.TestCase):
    def test_workingnomads(self):
        payload = [
            {
                "url": "https://www.workingnomads.com/job/go/1/",
                "title": "Software Engineer",
                "description": "<p>Build APIs with Python and PostgreSQL every day.</p>",
                "company_name": "Acme",
                "location": "USA",
                "pub_date": "2026-01-01",
                "tags": ["python"],
            }
        ]
        with patch("scraper.boards.extra_remote_portals.http_get", return_value=__import__("json").dumps(payload).encode()):
            jobs = WorkingNomadsParser().fetch_jobs_direct("Software Engineer", max_jobs=5)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["board"], "workingnomads")

    def test_himalayas(self):
        payload = {
            "jobs": [
                {
                    "title": "Backend Developer",
                    "companyName": "Co",
                    "locationRestrictions": "USA",
                    "description": "<p>Ship backend services with Go and Kubernetes.</p>",
                    "applicationLink": "https://himalayas.app/jobs/1",
                    "pubDate": "2026-01-01",
                }
            ],
            "nextCursor": None,
        }
        with patch("scraper.boards.extra_remote_portals.http_get", return_value=__import__("json").dumps(payload).encode()):
            jobs = HimalayasParser().fetch_jobs_direct("Backend Developer", max_jobs=3)
        self.assertEqual(len(jobs), 1)

    def test_jobspresso_rss(self):
        rss = b"""<?xml version="1.0"?><rss><channel><item>
<title>Software Engineer</title>
<link>https://jobspresso.co/job/x/</link>
<description><![CDATA[<p>Write TypeScript for a remote US product team daily.</p>]]></description>
</item></channel></rss>"""
        with patch("scraper.boards.feed_utils.http_get", return_value=rss):
            jobs = JobspressoParser().fetch_jobs_direct("Software Engineer", max_jobs=2)
        self.assertEqual(len(jobs), 1)


if __name__ == "__main__":
    unittest.main()
