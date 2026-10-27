"""Resolve the US remote scrape shard for scheduled GitHub Actions runs.

Four hourly slots rotate board groups and role sets so each pass stays inside
the ~22-minute run budget. A full cycle covers every board and both role sets
within four UTC hours; the schedule gate avoids duplicate work in the same hour.
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from pathlib import Path

FEED_BOARDS = (
    "remoteok,remotive,weworkremotely,himalayas,workingnomads,jobicy,"
    "jobspresso,arbeitnow"
)
BROWSER_BOARDS = (
    "dice,builtin,remote_co,dynamitejobs,justremote,arc,ziprecruiter,"
    "monster,careerbuilder,wellfound"
)
AGGREGATOR_BOARDS = "indeed,linkedin"

SLOTS: tuple[tuple[str, int], ...] = (
    (FEED_BOARDS, 1),
    (FEED_BOARDS, 2),
    (BROWSER_BOARDS, 1),
    (AGGREGATOR_BOARDS, 2),
)
SLOT_COUNT = len(SLOTS)


@dataclass(frozen=True)
class ScheduleSlot:
    index: int
    board: str
    country: str
    role_set: int


def resolve_slot(epoch_hour: int) -> ScheduleSlot:
    index = int(epoch_hour) % SLOT_COUNT
    boards, role_set = SLOTS[index]
    return ScheduleSlot(
        index=index,
        board=boards,
        country="US",
        role_set=role_set,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epoch-hour", type=int)
    parser.add_argument("--github-env", type=Path)
    args = parser.parse_args()

    epoch_hour = args.epoch_hour
    if epoch_hour is None:
        epoch_hour = int(time.time() // 3600)
    slot = resolve_slot(epoch_hour)
    lines = (
        f"JOB_SCRAPING_BOARDS={slot.board}",
        f"JOB_SCRAPING_COUNTRIES={slot.country}",
        f"US_REMOTE_ROLE_SET={slot.role_set}",
    )
    if args.github_env:
        with args.github_env.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
    else:
        print("\n".join(lines))
    print(
        f"US remote slot {slot.index}/{SLOT_COUNT - 1} -> "
        f"boards ({slot.board[:48]}...), {slot.country}, role set {slot.role_set}"
        if len(slot.board) > 48
        else f"US remote slot {slot.index}/{SLOT_COUNT - 1} -> "
        f"boards {slot.board}, {slot.country}, role set {slot.role_set}"
    )


if __name__ == "__main__":
    main()
