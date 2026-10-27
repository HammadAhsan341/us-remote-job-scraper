"""Resolve the US remote scrape shard for scheduled GitHub Actions runs.

Scheduled runs fire once per UTC hour (see schedule_gate.py). Every hour
scrapes all RSS/API feed boards with an alternating role set. Browser boards
run every 2 hours; Indeed/LinkedIn every 4 hours — so feed jobs refresh hourly
instead of waiting for a 4-hour slot rotation.
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

# Kept for tests/docs: legacy 4-slot names (feeds were split across two hours).
LEGACY_SLOT_COUNT = 4


@dataclass(frozen=True)
class ScheduleSlot:
    index: int
    board: str
    country: str
    role_set: int


def _dedupe_boards_csv(*groups: str) -> str:
    seen: set[str] = set()
    ordered: list[str] = []
    for group in groups:
        for raw in group.split(","):
            name = raw.strip().lower()
            if not name or name in seen:
                continue
            seen.add(name)
            ordered.append(name)
    return ",".join(ordered)


def resolve_slot(epoch_hour: int) -> ScheduleSlot:
    hour = int(epoch_hour)
    role_set = (hour % 2) + 1
    groups = [FEED_BOARDS]
    if hour % 2 == 0:
        groups.append(BROWSER_BOARDS)
    if hour % 4 == 0:
        groups.append(AGGREGATOR_BOARDS)
    board = _dedupe_boards_csv(*groups)
    return ScheduleSlot(
        index=hour % LEGACY_SLOT_COUNT,
        board=board,
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
    preview = slot.board if len(slot.board) <= 72 else f"{slot.board[:72]}..."
    print(
        f"US remote hour {epoch_hour}: role set {slot.role_set}, "
        f"boards ({len(slot.board.split(','))}): {preview}"
    )


if __name__ == "__main__":
    main()
