#!/usr/bin/env python3
"""Print Supabase job counts by job_source for market=us_remote."""

from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)

from services.supabase import get_supabase_service


def main() -> None:
    supabase = get_supabase_service()
    client = supabase.client
    rows = (
        client.table("jobs")
        .select("job_source")
        .eq("market", "us_remote")
        .execute()
        .data
        or []
    )
    counts = Counter((row.get("job_source") or "unknown").lower() for row in rows)
    print(f"US remote jobs in Supabase: {len(rows)}")
    print("-" * 40)
    for source, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"{count:5d}  {source}")
    print("-" * 40)


if __name__ == "__main__":
    main()
