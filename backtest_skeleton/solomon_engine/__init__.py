"""Solomon-method backtest engine — structural shell.

Each module maps to one role in the Solomon-method rule set:
  data       — ground-truth fetching with cache
  primitives — {SIGNAL_FEATURE} validation
  state      — state classification (range / trend / etc.)
  selector   — {ACTIVE_PAIR} and {MIDPOINT}
  simulate   — per-event forward walk with {EXIT_RULE}
  backtest   — orchestration loop
  report     — per-event + aggregate reporting

Fill in the # TODO blocks with your domain-specific rules.
"""
from .data import fetch_data, UNIT_SIZES
from .primitives import find_validated_primitives, Primitive
from .state import classify_state
from .selector import find_active_pair, midpoint
from .simulate import Event, simulate_event
from .backtest import run_backtest, BacktestResult
from .report import write_report

__all__ = [
    "fetch_data", "UNIT_SIZES",
    "find_validated_primitives", "Primitive",
    "classify_state",
    "find_active_pair", "midpoint",
    "Event", "simulate_event",
    "run_backtest", "BacktestResult",
    "write_report",
]
