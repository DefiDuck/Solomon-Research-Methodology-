"""Top-level backtest loop.

Walks every observation in the data window. At each observation:
  1. Find validated primitives in the lookback window.
  2. Find active pair around current value.
  3. Classify state (range / trend / undefined).
  4. Optionally apply state filter / window filter / higher-context filter.
  5. Apply entry rule (midpoint or rail).
  6. Open event with SL beyond opposite rail, TP at 1:1 RR.
  7. simulate_event → walk forward until exit.
  8. Move past event exit (no overlapping events).

The default time-stop N per granularity is set in DEFAULT_TIME_STOP. Override
via the `time_stop_n` argument.

Filters default to disabled. Phase-1 baseline reproduction is preserved when
all filter args are at their defaults.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time as dtime
from typing import Literal, Optional

import pandas as pd

from .data import fetch_data, get_unit_size
from .primitives import find_validated_primitives, Primitive
from .state import classify_state
from .selector import find_active_pair, midpoint
from .simulate import Event, simulate_event, compute_sl_from_pair


# TODO: fill in default time-stop N per granularity for your domain.
# Suggested derivation: from the visual evidence pass (Prompt 3), the empirical
# unit-count from {ENTRY_RULE} to typical exit at each granularity.
DEFAULT_TIME_STOP: dict[str, int] = {
    # "{GRANULARITY_A}": 18,
    # "{GRANULARITY_B}": 10,
    # "{GRANULARITY_C}": 6,
}

# TODO: fill in window definitions for your domain.
# Suggested: each named window is (start_time, end_time) in UTC.
# For temporal windows: use datetime.time. For non-temporal windows (e.g.
# "during release weeks"): swap the lookup for a domain-specific predicate.
WINDOWS_UTC: dict[str, tuple[dtime, dtime]] = {
    # "{WINDOW_A}": (dtime(0, 0), dtime(8, 0)),
    # "{WINDOW_B}": (dtime(8, 0), dtime(16, 0)),
}


def in_window(ts: pd.Timestamp, window: str) -> bool:
    """Is the timestamp inside the named window?"""
    if window not in WINDOWS_UTC:
        return False
    start, end = WINDOWS_UTC[window]
    t = ts.time() if ts.tzinfo is None else ts.tz_convert("UTC").time()
    if start <= end:
        return start <= t < end
    return t >= start or t < end


def label_window(ts: pd.Timestamp) -> str:
    """Best-fit single label for a timestamp."""
    for w in WINDOWS_UTC:
        if in_window(ts, w):
            return w
    return "off"


@dataclass
class BacktestResult:
    asset: str
    granularity: str
    start: str
    end: str
    entry_rule: str
    time_stop_n: int
    state_filter: str
    window_filter: list[str] | None
    bars_processed: int
    primitives_found: int
    events: list[Event] = field(default_factory=list)
    n_skipped_no_pair: int = 0
    n_skipped_state: int = 0
    n_skipped_window: int = 0
    data_range_actual: tuple[Optional[pd.Timestamp], Optional[pd.Timestamp]] = (None, None)

    def hit_rate(self) -> float:
        if not self.events:
            return 0.0
        wins = sum(1 for e in self.events if e.exit_reason == "tp_1r")
        return wins / len(self.events)

    def expectancy_units(self) -> float:
        if not self.events:
            return 0.0
        return sum(e.pnl_units for e in self.events) / len(self.events)

    def median_holding(self) -> float:
        if not self.events:
            return 0.0
        vals = sorted(e.holding_units for e in self.events)
        n = len(vals)
        if n % 2 == 1:
            return vals[n // 2]
        return (vals[n // 2 - 1] + vals[n // 2]) / 2

    def median_mfe(self) -> float:
        if not self.events:
            return 0.0
        vals = sorted(e.mfe_units for e in self.events)
        return vals[len(vals) // 2]

    def median_mae(self) -> float:
        if not self.events:
            return 0.0
        vals = sorted(e.mae_units for e in self.events)
        return vals[len(vals) // 2]


def run_backtest(
    asset: str,
    granularity: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    entry_rule: Literal["midpoint", "rail_lower", "rail_upper"] = "midpoint",
    time_stop_n: Optional[int] = None,
    state_filter: Literal["range", "trend", "any"] = "any",
    window_filter: Optional[list[str]] = None,
    source: str = "default",
    lookback: int = 200,
    support_tolerance: float = 1.0,
    primitives_refresh_every: int = 20,
    cooldown_bars: int = 3,
) -> BacktestResult:
    """Main backtest loop.

    Defaults reproduce the documented Phase 1 baseline. Phase 2 filter
    extensions (structural higher-context, density threshold, freshness, etc.)
    plug in via additional kwargs not shown here — keep them all default-disabled
    to preserve baseline reproducibility.
    """
    if time_stop_n is None:
        time_stop_n = DEFAULT_TIME_STOP.get(granularity, 10)

    unit_size = get_unit_size(asset)
    df = fetch_data(asset, granularity, start, end, source=source)

    result = BacktestResult(
        asset=asset, granularity=granularity, start=start or "", end=end or "",
        entry_rule=entry_rule, time_stop_n=time_stop_n,
        state_filter=state_filter, window_filter=window_filter,
        bars_processed=len(df), primitives_found=0,
    )
    if df.empty:
        return result
    result.data_range_actual = (df.index[0], df.index[-1])

    # Pre-compute primitives once at the start; refresh every N bars.
    primitives: list[Primitive] = find_validated_primitives(
        df, lookback=lookback, support_tolerance=support_tolerance,
        unit_size=unit_size, end_idx=lookback - 1,
    )
    result.primitives_found = len(primitives)
    next_refresh_idx = lookback + primitives_refresh_every

    skip_until = -1
    i = lookback
    while i < len(df) - 1:
        if i >= next_refresh_idx:
            primitives = find_validated_primitives(
                df, lookback=lookback, support_tolerance=support_tolerance,
                unit_size=unit_size, end_idx=i,
            )
            next_refresh_idx = i + primitives_refresh_every

        if i <= skip_until:
            i += 1
            continue

        # TODO: read the relevant value from df.iloc[i] for your domain.
        # For OHLC: value = df.iloc[i]['open']
        value = 0.0  # placeholder

        pair = find_active_pair(value, primitives)
        if pair is None:
            result.n_skipped_no_pair += 1
            i += 1
            continue
        lower, upper = pair
        mid = midpoint(pair)

        # State filter
        st = classify_state(df, i, lookback=50)
        if state_filter == "range" and st != "range":
            result.n_skipped_state += 1
            i += 1
            continue
        if state_filter == "trend" and st not in ("trend_up", "trend_down"):
            result.n_skipped_state += 1
            i += 1
            continue

        # Window filter
        ts = df.index[i]
        if window_filter:
            w = label_window(ts)
            if w not in window_filter:
                result.n_skipped_window += 1
                i += 1
                continue

        # TODO: implement entry trigger predicate per your entry_rule.
        # For "midpoint": fire when value just crossed the midpoint.
        # For "rail_lower": fire when value just touched the lower rail.
        # For "rail_upper": fire when value just touched the upper rail.
        direction = 0
        entry_value = 0.0

        if direction == 0:
            i += 1
            continue

        sl_value = compute_sl_from_pair(
            direction=direction,
            entry_value=entry_value,
            upper_rail=upper.value,
            lower_rail=lower.value,
            pad_units=2.0,
            unit_size=unit_size,
        )

        event = Event(
            entry_idx=i,
            entry_value=entry_value,
            direction=direction,
            sl_value=sl_value,
            time_stop_n=time_stop_n,
            entry_ts=ts,
            upper_rail=upper.value,
            lower_rail=lower.value,
            midpoint_at_entry=mid,
            state_at_entry=st,
            window_at_entry=label_window(ts),
            asset=asset,
            granularity=granularity,
        )
        simulate_event(df, event, unit_size=unit_size)
        result.events.append(event)
        skip_until = (event.exit_idx or i) + cooldown_bars
        i = skip_until + 1

    return result
