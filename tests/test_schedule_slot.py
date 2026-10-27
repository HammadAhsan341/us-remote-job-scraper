import unittest

from scripts.schedule_slot import (
    AGGREGATOR_BOARDS,
    BROWSER_BOARDS,
    FEED_BOARDS,
    resolve_slot,
)


class TestScheduleSlot(unittest.TestCase):
    def test_every_hour_includes_all_feed_boards(self):
        for hour in (100, 101, 102, 103):
            slot = resolve_slot(hour)
            for board in FEED_BOARDS.split(","):
                self.assertIn(board, slot.board.split(","))

    def test_role_set_alternates_each_hour(self):
        self.assertEqual(resolve_slot(10).role_set, 1)
        self.assertEqual(resolve_slot(11).role_set, 2)
        self.assertEqual(resolve_slot(12).role_set, 1)

    def test_browser_boards_every_two_hours(self):
        even = resolve_slot(200)
        odd = resolve_slot(201)
        self.assertIn("dice", even.board)
        self.assertNotIn("dice", odd.board)

    def test_aggregators_every_four_hours(self):
        self.assertIn("indeed", resolve_slot(400).board)
        self.assertNotIn("indeed", resolve_slot(401).board)
        self.assertIn("indeed", resolve_slot(404).board)

    def test_hour_four_includes_feeds_browser_and_aggregators(self):
        slot = resolve_slot(404)
        self.assertIn("remoteok", slot.board)
        self.assertIn("dice", slot.board)
        self.assertIn("indeed", slot.board)


if __name__ == "__main__":
    unittest.main()
