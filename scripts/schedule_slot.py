"""Resolve the US remote scrape shard (role set rotation only)."""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from pathlib import Path

ALL_BOARDS = (
    "remoteok,remotive,weworkremotely,himalayas,workingnomads,jobicy,jobspresso,"
    "arbeitnow,dice,builtin,remote_co,dynamitejobs,justremote,arc,ziprecruiter,"
    "monster,careerbuilder,wellfound,indeed,linkedin"
)
SLOT_COUNT = 2


@dataclass(frozen=True)
class ScheduleSlot:
    index: int
    board: str
    country: str
    role_set: int


def resolve_slot(epoch_hour: int) -> ScheduleSlot:
    index = int(epoch_hour) % SLOT_COUNT
    return ScheduleSlot(
        index=index,
        board=ALL_BOARDS,
        country="US",
        role_set=index + 1,
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
        f"all US remote boards, {slot.country}, role set {slot.role_set}"
    )


if __name__ == "__main__":
    main()
