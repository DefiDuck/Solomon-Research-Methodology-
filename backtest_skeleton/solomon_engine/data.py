"""Ground-truth data fetching.

Default source: domain-specific (your adapter goes here).
Optional: extended-history adapter (e.g. paid API).

Cache: a parquet file per (asset, granularity, start, end, source) tuple.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

import pandas as pd


# TODO: fill in unit sizes for your domain.
# A unit size is the smallest meaningful increment of a measurement in your domain.
# For numeric/continuous domains it's typically the minimum tick of the underlying
# series; for discrete/textual domains it's typically just 1.
UNIT_SIZES: dict[str, float] = {
    # "{ASSET_A}": 1.0,
    # "{ASSET_B}": 0.01,
}


_CACHE_DIR = Path(__file__).resolve().parent.parent / "runs" / "_data_cache"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_key(asset: str, granularity: str, start: str, end: str, source: str) -> Path:
    raw = f"{source}|{asset}|{granularity}|{start}|{end}"
    h = hashlib.sha1(raw.encode()).hexdigest()[:12]
    safe = "".join(c if c.isalnum() else "_" for c in asset)
    return _CACHE_DIR / f"{safe}_{granularity}_{h}.parquet"


def fetch_data(
    asset: str,
    granularity: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    source: str = "default",
    use_cache: bool = True,
) -> pd.DataFrame:
    """Fetch domain ground-truth data.

    Returns DataFrame with at minimum:
      - timestamp index (UTC, tz-aware)
      - whatever measurements your domain needs (e.g. open/high/low/close/volume
        for prices, or whatever the equivalent is for your domain)

    For non-financial domains, the columns and concept of "high/low/close" may
    not apply. Adapt to your domain. The minimum is: a timestamp + the values
    your primitives.py needs.

    Args:
        asset: domain-specific identifier
        granularity: one of your allowed granularities
        start, end: ISO date strings (optional; default = adapter's default range)
        source: which adapter to use
        use_cache: read from cache if available

    Returns:
        DataFrame, or empty DataFrame if fetch fails.
    """
    cache_path = _cache_key(asset, granularity, start or "", end or "", source)
    if use_cache and cache_path.exists():
        return pd.read_parquet(cache_path)

    if source == "default":
        df = _fetch_default(asset, granularity, start, end)
    elif source == "extended":
        df = _fetch_extended(asset, granularity, start, end)
    else:
        raise ValueError(f"unknown source: {source}")

    if df is None or df.empty:
        return pd.DataFrame()

    if use_cache:
        try:
            df.to_parquet(cache_path)
        except Exception:
            pass
    return df


def _fetch_default(asset: str, granularity: str, start: Optional[str], end: Optional[str]) -> pd.DataFrame:
    """The default adapter for your domain.

    TODO: implement using your data source's API. Document its limits:
      - max history per granularity
      - rate limits
      - any auth requirements
    """
    raise NotImplementedError(
        "Implement your domain's default data adapter. "
        "See requirements.txt for suggested libraries."
    )


def _fetch_extended(asset: str, granularity: str, start: Optional[str], end: Optional[str]) -> pd.DataFrame:
    """The extended-history adapter (typically a paid API).

    TODO: implement if you have a paid adapter. Otherwise leave as stub.
    """
    raise NotImplementedError("Optional: implement extended-history adapter.")


def get_unit_size(asset: str) -> float:
    """Return the unit size for the asset, defaulting to 0.01 if unknown."""
    return UNIT_SIZES.get(asset, 0.01)
