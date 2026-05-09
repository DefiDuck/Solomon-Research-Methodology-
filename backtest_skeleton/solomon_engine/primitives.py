"""{SIGNAL_FEATURE} validation.

Per your "primitive validation" Finding (typically of the form "a feature is
valid only if it has N same-type supports").

Implementation: scan the data sequence, identify candidate "support points"
of each type, cluster them by value within tolerance, and accept clusters
with ≥N same-type members.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal

import pandas as pd


@dataclass
class Primitive:
    value: float
    support_type: Literal["wick", "body"]   # rename to your domain's types
    n_supports: int
    first_support_idx: int
    last_support_idx: int

    def __repr__(self) -> str:
        return (
            f"Primitive(value={self.value:.5f}, type={self.support_type}, "
            f"supports={self.n_supports}, first={self.first_support_idx}, "
            f"last={self.last_support_idx})"
        )


def find_validated_primitives(
    df: pd.DataFrame,
    lookback: int = 200,
    support_tolerance: float = 0.5,
    unit_size: float = 0.01,
    end_idx: int | None = None,
) -> List[Primitive]:
    """Return list of Primitive objects with ≥N same-type supports.

    Args:
        df: data DataFrame.
        lookback: number of bars to scan (most recent N before end_idx).
        support_tolerance: cluster tolerance in units (e.g. 0.5 = half a unit).
        unit_size: domain unit size.
        end_idx: last bar index to include (default: len(df)-1).

    Mixed types are NOT counted in the same primitive — each primitive is
    purely-typeA or purely-typeB.

    TODO:
      - Decide how many supports define a "validated" primitive (typically 3
        per a single-mention Finding from a high-trust channel).
      - Decide what counts as a "support point" in your domain.
      - Decide the clustering tolerance.

    The default returned list is empty. Fill in the body to extract supports
    and cluster.
    """
    if df.empty:
        return []

    if end_idx is None:
        end_idx = len(df) - 1
    start_idx = max(0, end_idx - lookback + 1)
    window = df.iloc[start_idx : end_idx + 1].copy()

    if len(window) == 0:
        return []

    # TODO: define support_points = list of (value, type, original_idx) tuples
    support_points: list[tuple[float, str, int]] = []

    # TODO: cluster support_points by value within `support_tolerance * unit_size`
    # TODO: filter clusters to those with ≥ N same-type members (where N is
    #       defined by your Finding — typically 3)
    # TODO: build Primitive objects from each accepted cluster

    return []
