"""Per-event simulation.

An `Event` is opened at some bar idx with entry/SL/direction/time-stop set,
then walked forward bar-by-bar. Exit conditions checked each bar in this
priority:

  1. SL hit  (boundary backstop violated)
  2. TP hit  (1:1 RR target reached)
  3. Time   (time_stop_n bars elapsed — primary exit per the canonical rule)
  4. End of data

Both intra-bar and close-based checks are conservative — SL is checked against
the bar's adverse extreme (high for short, low for long), so we assume the
worst-case wick hit it.

Per the canonical Solomon-method exit rule: TIME stop is the primary exit;
price/value SL is a backstop only.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class Event:
    entry_idx: int
    entry_value: float
    direction: int             # +1 long-equivalent, -1 short-equivalent
    sl_value: float
    time_stop_n: int           # max units to hold

    tp_value: Optional[float] = None  # if None, computed as 1:1 RR

    # Filled by simulate_event
    exit_idx: Optional[int] = None
    exit_value: Optional[float] = None
    exit_reason: Optional[str] = None  # 'sl' | 'tp_1r' | 'time' | 'end_of_data'
    mfe_units: float = 0.0
    mae_units: float = 0.0
    holding_units: int = 0
    pnl_units: float = 0.0      # signed pnl at exit, in domain units

    # Context (for reporting)
    entry_ts: Optional[pd.Timestamp] = None
    upper_rail: Optional[float] = None
    lower_rail: Optional[float] = None
    midpoint_at_entry: Optional[float] = None
    state_at_entry: Optional[str] = None
    window_at_entry: Optional[str] = None
    asset: Optional[str] = None
    granularity: Optional[str] = None


def simulate_event(df: pd.DataFrame, event: Event, unit_size: float = 0.01) -> Event:
    """Walk forward from event.entry_idx until exit. Mutate `event` and return.

    TODO:
      - Decide what columns of df define the bar's adverse and favorable
        extremes. For OHLC it's high and low. For text-corpus it might be
        max/min sentiment in the bar window.
      - Decide whether SL or TP wins when both hit in the same bar (engine
        defaults to SL; alternative is to mark exit_reason='ambiguous').
    """
    if event.tp_value is None:
        risk = abs(event.entry_value - event.sl_value)
        event.tp_value = event.entry_value + event.direction * risk

    n = len(df)
    last_idx = min(event.entry_idx + event.time_stop_n, n - 1)

    for i in range(event.entry_idx + 1, last_idx + 1):
        bar = df.iloc[i]
        # TODO: define `favorable_extreme` and `adverse_extreme` per your domain.
        # For OHLC long: favorable = bar['high'], adverse = bar['low'].
        # For OHLC short: favorable = bar['low'],  adverse = bar['high'].
        favorable_extreme = 0.0  # placeholder
        adverse_extreme = 0.0    # placeholder

        # Track favorable / adverse excursion in domain units
        if event.direction == 1:
            mfe_now = (favorable_extreme - event.entry_value) / unit_size
            mae_now = (event.entry_value - adverse_extreme) / unit_size
        else:
            mfe_now = (event.entry_value - favorable_extreme) / unit_size
            mae_now = (adverse_extreme - event.entry_value) / unit_size

        if mfe_now > event.mfe_units:
            event.mfe_units = mfe_now
        if mae_now > event.mae_units:
            event.mae_units = mae_now

        # TODO: define sl_hit and tp_hit predicates from the bar's extremes
        sl_hit = False
        tp_hit = False

        # Conservative tie-break: SL wins if both hit in the same bar.
        if sl_hit:
            event.exit_idx = i
            event.exit_value = event.sl_value
            event.exit_reason = "sl"
            break
        if tp_hit:
            event.exit_idx = i
            event.exit_value = event.tp_value
            event.exit_reason = "tp_1r"
            break
    else:
        # Loop completed without break — time stop or end of data
        if last_idx >= n - 1 and event.entry_idx + event.time_stop_n > n - 1:
            event.exit_idx = last_idx
            event.exit_reason = "end_of_data"
        else:
            event.exit_idx = last_idx
            event.exit_reason = "time"
        # TODO: derive exit_value from df.iloc[event.exit_idx]
        event.exit_value = event.entry_value  # placeholder

    event.holding_units = (event.exit_idx or event.entry_idx) - event.entry_idx
    event.pnl_units = (event.exit_value - event.entry_value) * event.direction / unit_size
    return event


def compute_sl_from_pair(
    direction: int,
    entry_value: float,
    upper_rail: float,
    lower_rail: float,
    pad_units: float = 1.0,
    unit_size: float = 0.01,
) -> float:
    """Default SL placement: just past the opposite rail.

    For direction=+1: SL = lower_rail - pad
    For direction=-1: SL = upper_rail + pad

    Implements the canonical rule: "boundary backstop only — just beyond the
    opposite rail of the active pair."
    """
    pad = pad_units * unit_size
    if direction == 1:
        return lower_rail - pad
    return upper_rail + pad
