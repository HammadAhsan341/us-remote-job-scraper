"""US remote scheduled shards: parallel feed jobs + optional browser/aggregators."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path

from scripts.schedule_gate import HALF_HOUR_SECONDS

FEEDS_A = "remoteok,remotive,weworkremotely,himalayas"
FEEDS_B = "workingnomads,jobicy,jobspresso,arbeitnow"
BROWSER_BOARDS = (
    "dice,builtin,remote_co,dynamitejobs,justremote,arc,ziprecruiter,"
    "monster,careerbuilder,wellfound"
)
AGGREGATOR_BOARDS = "indeed,linkedin"

SHARD_BOARDS: dict[str, str] = {
    "feeds_a": FEEDS_A,
    "feeds_b": FEEDS_B,
    "browser": BROWSER_BOARDS,
    "aggregators": AGGREGATOR_BOARDS,
}

FEED_BOARDS = f"{FEEDS_A},{FEEDS_B}"
LEGACY_SLOT_COUNT = 4


@dataclass(frozen=True)
class ScheduleSlot:
    index: int
    board: str
    country: str
    role_set: int


def scheduled_shards(epoch_half_hour: int) -> list[str]:
    half = int(epoch_half_hour)
    shards = ["feeds_a", "feeds_b"]
    if half % 2 == 0:
        shards.append("browser")
    if half % 4 == 0:
        shards.append("aggregators")
    return shards


def boards_for_shard(epoch_half_hour: int, shard: str) -> str:
    if shard not in scheduled_shards(epoch_half_hour):
        return ""
    return SHARD_BOARDS.get(shard, "")


def resolve_slot(epoch_half_hour: int) -> ScheduleSlot:
    """Combined board list (legacy / tests)."""
    half = int(epoch_half_hour)
    parts = [boards_for_shard(half, name) for name in scheduled_shards(half)]
    board = ",".join(p for p in parts if p)
    return ScheduleSlot(
        index=half % LEGACY_SLOT_COUNT,
        board=board,
        country="US",
        role_set=(half % 2) + 1,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epoch-half-hour", type=int)
    parser.add_argument("--epoch-hour", type=int, help="Deprecated")
    parser.add_argument("--shard", type=str, default="")
    parser.add_argument("--plan-matrix", action="store_true")
    parser.add_argument("--github-env", type=Path)
    args = parser.parse_args()

    if args.epoch_half_hour is not None:
        epoch_half = int(args.epoch_half_hour)
    elif args.epoch_hour is not None:
        epoch_half = int(args.epoch_hour) * 2
    else:
        epoch_half = int(time.time() // HALF_HOUR_SECONDS)

    if args.plan_matrix:
        print(json.dumps({"shard": scheduled_shards(epoch_half)}))
        return

    if args.shard:
        boards = boards_for_shard(epoch_half, args.shard.strip())
        if not boards:
            print(f"Shard {args.shard} inactive for half-hour {epoch_half}")
            return
        lines = (
            f"JOB_SCRAPING_BOARDS={boards}",
            f"JOB_SCRAPING_COUNTRIES=US",
            f"US_REMOTE_ROLE_SET={(epoch_half % 2) + 1}",
        )
        if args.github_env:
            with args.github_env.open("a", encoding="utf-8") as handle:
                handle.write("\n".join(lines) + "\n")
        else:
            print("\n".join(lines))
        return

    slot = resolve_slot(epoch_half)
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
        f"US remote half-hour {epoch_half}: role set {slot.role_set}, "
        f"boards ({len(slot.board.split(','))}): {preview}"
    )


if __name__ == "__main__":
    main()
