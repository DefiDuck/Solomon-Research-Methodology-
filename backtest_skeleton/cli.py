"""CLI entry point.

Usage:
    python cli.py --asset {ASSET} --granularity {GRANULARITY} \
                  --start 2026-03-01 --end 2026-05-06 \
                  --entry-rule midpoint --window {WINDOW_A},{WINDOW_B} \
                  --time-stop 10 --run-id smoke_test
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from solomon_engine.backtest import run_backtest
from solomon_engine.report import write_report


def main() -> int:
    p = argparse.ArgumentParser(description="Solomon-method backtest engine (skeleton)")
    p.add_argument("--asset", required=True)
    p.add_argument("--granularity", required=True)
    p.add_argument("--start", default=None)
    p.add_argument("--end", default=None)
    p.add_argument(
        "--entry-rule",
        default="midpoint",
        choices=["midpoint", "rail_lower", "rail_upper"],
    )
    p.add_argument(
        "--state-filter",
        default="any",
        choices=["range", "trend", "any"],
    )
    p.add_argument("--window", default=None, help="comma-separated window names")
    p.add_argument("--time-stop", type=int, default=None)
    p.add_argument("--lookback", type=int, default=200)
    p.add_argument("--support-tol", type=float, default=1.0)
    p.add_argument("--source", default="default")
    p.add_argument("--run-id", required=True)
    args = p.parse_args()

    windows = args.window.split(",") if args.window else None

    t0 = time.time()
    result = run_backtest(
        asset=args.asset,
        granularity=args.granularity,
        start=args.start,
        end=args.end,
        entry_rule=args.entry_rule,
        time_stop_n=args.time_stop,
        state_filter=args.state_filter,
        window_filter=windows,
        source=args.source,
        lookback=args.lookback,
        support_tolerance=args.support_tol,
    )
    dt = time.time() - t0

    out_dir = write_report(result, args.run_id)

    n = len(result.events)
    wr = result.hit_rate() * 100
    print(
        f"Run {args.run_id}: {n} events, {wr:.1f}% hit rate, "
        f"exp={result.expectancy_units():+.2f} units ({dt:.1f}s) → {out_dir}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
