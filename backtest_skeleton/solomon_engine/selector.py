"""{ACTIVE_PAIR} selection + {MIDPOINT}.

Per the canonical Solomon-method rule: at any moment, the "active pair" is
the two adjacent validated primitives (one above, one below) bounding the
current observation. The midpoint is the 50% mark between them.

Both midpoint and rail entries are valid — the orchestration loop sweeps
between them.
"""
from __future__ import annotations

from typing import Optional, Tuple

from .primitives import Primitive


def find_active_pair(value: float, primitives: list[Primitive]) -> Optional[Tuple[Primitive, Primitive]]:
    """Return (lower, upper) — the two adjacent primitives bounding `value`.

    Returns None if `value` is below all primitives or above all of them
    (no active pair exists at this state).

    If two primitives sit at the same value (different support types), the
    most-supported one is preferred.
    """
    if not primitives:
        return None
    sorted_primitives = sorted(primitives, key=lambda p: p.value)

    lower: Optional[Primitive] = None
    upper: Optional[Primitive] = None
    for p in sorted_primitives:
        if p.value <= value:
            if lower is None or p.value > lower.value or (
                p.value == lower.value and p.n_supports > lower.n_supports
            ):
                lower = p
        elif p.value > value and upper is None:
            upper = p
            break

    if lower is None or upper is None:
        return None
    return (lower, upper)


def midpoint(pair: Tuple[Primitive, Primitive]) -> float:
    """50% midpoint of the active pair."""
    return (pair[0].value + pair[1].value) / 2.0


def box_height(pair: Tuple[Primitive, Primitive]) -> float:
    """Vertical span between rails — useful for tolerance checks."""
    return pair[1].value - pair[0].value
