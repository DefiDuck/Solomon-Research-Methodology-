"""Per-event and aggregate reporting.

Writes three files per backtest run:
  runs/{run_id}/events.csv        — per-event row table
  runs/{run_id}/summary.json      — aggregate metrics
  runs/{run_id}/report.md         — human-readable summary
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd

from .backtest import BacktestResult


_RUNS_ROOT = Path(__file__).resolve().parent.parent / "runs"


def write_report(result: BacktestResult, run_id: str) -> Path:
    """Write CSV + JSON + Markdown for the run. Return the run directory."""
    run_dir = _RUNS_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Per-event CSV
    rows = []
    for e in result.events:
        rows.append({
            "entry_ts": e.entry_ts.isoformat() if e.entry_ts is not None else "",
            "entry_idx": e.entry_idx,
            "exit_idx": e.exit_idx,
            "direction": "long" if e.direction == 1 else "short",
            "entry_value": round(e.entry_value, 6),
            "sl_value": round(e.sl_value, 6),
            "tp_value": round(e.tp_value, 6) if e.tp_value else None,
            "exit_value": round(e.exit_value, 6) if e.exit_value else None,
            "exit_reason": e.exit_reason,
            "holding_units": e.holding_units,
            "pnl_units": round(e.pnl_units, 2),
            "mfe_units": round(e.mfe_units, 2),
            "mae_units": round(e.mae_units, 2),
            "lower_rail": round(e.lower_rail, 6) if e.lower_rail else None,
            "upper_rail": round(e.upper_rail, 6) if e.upper_rail else None,
            "midpoint": round(e.midpoint_at_entry, 6) if e.midpoint_at_entry else None,
            "state": e.state_at_entry,
            "window": e.window_at_entry,
        })
    events_df = pd.DataFrame(rows)
    events_csv = run_dir / "events.csv"
    events_df.to_csv(events_csv, index=False)

    # Aggregate JSON
    summary = _summary_dict(result)
    summary_path = run_dir / "summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    # Human-readable Markdown
    md = _markdown_report(result, summary, run_id)
    md_path = run_dir / "report.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write(md)

    return run_dir


def _summary_dict(r: BacktestResult) -> dict:
    n = len(r.events)
    wins = sum(1 for e in r.events if e.exit_reason == "tp_1r")
    losses = sum(1 for e in r.events if e.exit_reason == "sl")
    timeouts = sum(1 for e in r.events if e.exit_reason == "time")
    eod = sum(1 for e in r.events if e.exit_reason == "end_of_data")

    by_window: dict[str, int] = Counter(e.window_at_entry for e in r.events)
    by_state: dict[str, int] = Counter(e.state_at_entry for e in r.events)
    by_direction: dict[str, int] = Counter("long" if e.direction == 1 else "short" for e in r.events)

    hit_rate_per_window = {}
    for w in by_window:
        n_w = by_window[w]
        wins_w = sum(1 for e in r.events if e.window_at_entry == w and e.exit_reason == "tp_1r")
        hit_rate_per_window[w] = round(wins_w / n_w, 3) if n_w else 0.0

    def safe_actual(idx):
        v = r.data_range_actual[idx]
        return v.isoformat() if v is not None else None

    return {
        "asset": r.asset,
        "granularity": r.granularity,
        "start_requested": r.start,
        "end_requested": r.end,
        "data_first_bar": safe_actual(0),
        "data_last_bar": safe_actual(1),
        "bars_processed": r.bars_processed,
        "primitives_found": r.primitives_found,
        "entry_rule": r.entry_rule,
        "time_stop_n": r.time_stop_n,
        "state_filter": r.state_filter,
        "window_filter": r.window_filter,
        "n_events": n,
        "n_wins": wins,
        "n_losses": losses,
        "n_timeouts": timeouts,
        "n_end_of_data": eod,
        "hit_rate": round(r.hit_rate(), 3),
        "expectancy_units": round(r.expectancy_units(), 2),
        "median_holding": r.median_holding(),
        "median_mfe": round(r.median_mfe(), 2),
        "median_mae": round(r.median_mae(), 2),
        "by_window": dict(by_window),
        "by_state": dict(by_state),
        "by_direction": dict(by_direction),
        "hit_rate_by_window": hit_rate_per_window,
        "n_skipped_no_pair": r.n_skipped_no_pair,
        "n_skipped_state": r.n_skipped_state,
        "n_skipped_window": r.n_skipped_window,
    }


def _markdown_report(r: BacktestResult, s: dict, run_id: str) -> str:
    n = s["n_events"]
    wr = s["hit_rate"]

    lines = []
    lines.append(f"# Backtest report — {run_id}")
    lines.append("")
    lines.append(f"**Asset / granularity:** `{s['asset']}` / `{s['granularity']}`")
    lines.append(f"**Data range (actual):** {s['data_first_bar']} → {s['data_last_bar']}")
    lines.append(f"**Bars processed:** {s['bars_processed']}")
    lines.append(f"**Primitives found (initial):** {s['primitives_found']}")
    lines.append("")
    lines.append("**Configuration:**")
    lines.append(f"- Entry rule: `{s['entry_rule']}`")
    lines.append(f"- Time-stop N: {s['time_stop_n']}")
    lines.append(f"- State filter: `{s['state_filter']}`")
    lines.append(f"- Window filter: {s['window_filter'] or '— (all windows)'}")
    lines.append("")
    lines.append("## Aggregate metrics")
    lines.append("")
    lines.append(f"- **Events:** {n}")
    lines.append(f"- **Wins / Losses / Timeouts / EOD:** {s['n_wins']} / {s['n_losses']} / {s['n_timeouts']} / {s['n_end_of_data']}")
    lines.append(f"- **Hit rate:** {wr*100:.1f}%")
    lines.append(f"- **Expectancy / event:** {s['expectancy_units']:+.2f} units")
    lines.append(f"- **Median holding:** {s['median_holding']} units")
    lines.append(f"- **Median MFE / MAE:** {s['median_mfe']} / {s['median_mae']} units")
    lines.append("")
    lines.append("## Distribution")
    lines.append("")
    lines.append(f"- By window: {s['by_window']}")
    lines.append(f"- By state: {s['by_state']}")
    lines.append(f"- By direction: {s['by_direction']}")
    if s["hit_rate_by_window"]:
        lines.append("")
        lines.append("**Hit rate per window:**")
        for w, rate in sorted(s["hit_rate_by_window"].items()):
            lines.append(f"- `{w}`: {rate*100:.1f}%")
    lines.append("")
    lines.append("## Skip counters")
    lines.append("")
    lines.append(f"- No active pair: {s['n_skipped_no_pair']}")
    lines.append(f"- State filter: {s['n_skipped_state']}")
    lines.append(f"- Window filter: {s['n_skipped_window']}")
    lines.append("")
    lines.append("## Files")
    lines.append("")
    lines.append("- `events.csv` — per-event row table")
    lines.append("- `summary.json` — full aggregate metrics")
    lines.append("- `report.md` — this file")

    return "\n".join(lines) + "\n"
