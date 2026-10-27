import unittest

from core.settings import DEFAULT_BOARDS
from main import _role_searches
from scraper.boards.linkedin import LinkedInParser
from tests.test_scrape_resilience import _settings

US_REMOTE = "Remote, United States"


class TestRemoteRoleSearches(unittest.TestCase):
    def test_each_active_board_gets_one_remote_us_pass(self):
        settings = _settings(job_scraping_boards=["remoteok", "indeed", "linkedin"])
        self.assertEqual(
            _role_searches("Software Engineer", settings),
            [
                ("remoteok", US_REMOTE),
                ("indeed", US_REMOTE),
                ("linkedin", US_REMOTE),
            ],
        )

    def test_disabled_gulf_boards_are_not_in_default_all(self):
        from core.settings import _parse_boards

        parsed = _parse_boards("all")
        self.assertEqual(parsed, DEFAULT_BOARDS)
        self.assertNotIn("bayt", parsed)


class TestLinkedInRemoteUrl(unittest.TestCase):
    def test_remote_us_search_uses_remote_location(self):
        url = LinkedInParser().build_search_url(
            "Software Engineer", "Remote, United States", 1
        )
        self.assertIn("keywords=Software", url.replace("+", " "))
        self.assertIn("United", url)


if __name__ == "__main__":
    unittest.main()
