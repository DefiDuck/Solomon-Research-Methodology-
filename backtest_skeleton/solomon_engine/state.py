"""State classification.

Per your "state rule" Finding (typically of the form: a state is identified
when subsequent observations either contain or break a reference observation
along a documented dimension).

Returns one of:
  "range"      — observations stayed bounded by the reference
  "trend_up"   — observations broke past the reference upward
  "trend_down" — observations broke past the reference downward
  "undefined"  — too little data, or mixed breaks in both directions
"""
from __future__ import annotations

from typing import Literal

import pandas as pd


State = Literal["range", "trend_up", "trend_down", "undefined"]


def classify_state(df: pd.DataFrame, idx: int, lookback: int = 50) -> State:
    """Classify the state at index `idx` using the prior `lookback` observations.

    The reference observation is the bar `lookback` steps back. We then count
    how many bars between (reference+1, idx) closed above or below the
    reference's "body" (or domain-equivalent containment region).

    Args:
        df: data DataFrame from data.py.
        idx: current observation index.
        lookback: how far back the reference is.

    Returns:
        One of: "range" / "trend_up" / "trend_down" / "undefined".

    TODO:
      - Decide what "body" means in your domain. For OHLC it's max(open, close)
        and min(open, close). For text-corpus it might be the dominant feature
        of the reference observation.
      - Decide whether wicks (extremes that don't close past the reference)
        count as breaks. Per the canonical Solomon-method state rule, wicks
        do NOT break a range — only body closes do.
    """
    if idx <= 0 or df.empty:
        return "undefined"

    origin_idx = max(0, idx - lookback)
    if origin_idx >= idx:
        return "undefined"

    # TODO: define `body_top` and `body_bot` from df.iloc[origin_idx]
    # body_top = ...
    # body_bot = ...

    # TODO: walk bars from origin_idx+1 to idx, count up_breaks / down_breaks
    up_breaks = 0
    down_breaks = 0

    if up_breaks == 0 and down_breaks == 0:
        return "range"
    if up_breaks > 0 and down_breaks == 0:
        return "trend_up"
    if down_breaks > 0 and up_breaks == 0:
        return "trend_down"
    return "undefined"


def trend_filter(df: pd.DataFrame, idx: int, ma_period: int = 20) -> Literal["up", "down", "flat"]:
    """Simple MA-slope direction filter (a coarse alternative to structural detection).

    Use the structural HH/HL filter (see filters.py if you've built it) instead
    of this in production — it's much more selective. This is here only as a
    weak baseline you can compare against.
    """
    if idx < ma_period + 5 or df.empty:
        return "flat"
    # TODO: compute MA over the last ma_period observations and compare to a
    # prior MA window to determine direction.
    return "flat"
