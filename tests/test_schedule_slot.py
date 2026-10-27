import unittest

from scripts.schedule_slot import FEED_BOARDS, SLOTS, resolve_slot


class TestScheduleSlot(unittest.TestCase):
    def test_four_slot_rotation(self):
        s0 = resolve_slot(100)
        s1 = resolve_slot(101)
        self.assertEqual(s0.index, 0)
        self.assertEqual(s1.index, 1)
        self.assertEqual(s0.board, FEED_BOARDS)
        self.assertEqual(s0.role_set, 1)
        self.assertEqual(s1.role_set, 2)

    def test_full_cycle_covers_aggregators(self):
        boards = {resolve_slot(200 + i).board for i in range(len(SLOTS))}
        self.assertIn("indeed,linkedin", boards)
        self.assertEqual(len(SLOTS), 4)


if __name__ == "__main__":
    unittest.main()
