import unittest

from scripts.schedule_slot import (
    AGGREGATOR_BOARDS,
    FEED_BOARDS,
    boards_for_shard,
    resolve_slot,
    scheduled_shards,
)


class TestScheduleSlot(unittest.TestCase):
    def test_every_half_hour_includes_all_feed_boards(self):
        for half in (100, 101, 102, 103):
            slot = resolve_slot(half)
            for board in FEED_BOARDS.split(","):
                self.assertIn(board, slot.board.split(","))

    def test_role_set_alternates_each_half_hour(self):
        self.assertEqual(resolve_slot(10).role_set, 1)
        self.assertEqual(resolve_slot(11).role_set, 2)

    def test_browser_shard_every_two_half_hours(self):
        self.assertIn("dice", boards_for_shard(200, "browser"))
        self.assertEqual(boards_for_shard(201, "browser"), "")

    def test_aggregators_shard_every_four_half_hours(self):
        self.assertIn("indeed", boards_for_shard(400, "aggregators"))
        self.assertEqual(boards_for_shard(401, "aggregators"), "")

    def test_plan_matrix_includes_feed_shards_always(self):
        shards = scheduled_shards(101)
        self.assertIn("feeds_a", shards)
        self.assertIn("feeds_b", shards)

    def test_half_four_includes_aggregators_in_plan(self):
        shards = scheduled_shards(404)
        self.assertIn("aggregators", shards)
        self.assertIn("browser", shards)


if __name__ == "__main__":
    unittest.main()
