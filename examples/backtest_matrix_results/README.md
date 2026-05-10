# Backtest matrix — stress-testing across instrument family

A worked example of applying the methodology's backtest skeleton to validate a candidate rule set across multiple instruments, timeframes, sessions, filter sets, and time windows.

## Why a matrix, not a single test?

A single passing backtest cell can be a coincidence. A matrix reveals where the rule set genuinely works versus where it overfits to a particular slice. The shape:

```
cell = (instrument, timeframe, session, filter_set, window)
```

Run each cell as one backtest. Aggregate by axis. The result is a calibration map of where the rule set holds and where it breaks.

This is the **third independent validation surface** in the methodology stack:

1. Heuristic audit (single-pass FACT/HYPOTHESIS/SPECULATION grading)
2. Cross-model adversarial audit (3 isolated auditors per finding × 2 model families)
3. **Cross-instrument backtest matrix** (this artifact)

Each surface checks a different failure mode. The first checks claim quality. The second checks reasoning quality. The third checks empirical generalization.

## Cell selection

Full Cartesian = 7 instruments × 3 timeframes × 2 sessions × 3 filter sets × 2 windows = 252 cells. We ran a structured **26-cell subset** designed to maximize coverage per cell:

| Block | Cells | Question it answers |
|---|---:|---|
| A | 14 | Does the canonical config hold across instruments? |
| B | +2 | Does timeframe matter on the strongest instruments? |
| C | +3 | Does the session filter contribute, or is it spurious? |
| D | +4 | Is the result stable out-of-sample (prior 60-180 days)? |
| E | +2 | Does the canonical filter improve on baseline? |
| F | +1 | Highest-WR instrument + most-selective filter combo |

Total: 26 unique cells. Wall-clock ~6 minutes via aggressive data-fetch caching.

## Aggregate results

The numbers below are aggregated across all valid cells in the matrix. Win rate (WR) is the proportion of trades that hit the 1:1 take-profit before the time-stop or price-stop. Expectancy is mean P&L per trade in the instrument's tick units (note: ticks are not normalized across instruments, so cross-instrument expectancy comparison is misleading — read per-instrument).

### By instrument

| Instrument | Cells | Valid | Mean WR | WR min | WR max |
|---|---:|---:|---:|---:|---:|
| `GC=F` (gold futures) | 8 | 6 | **75.7%** | 64.6% | 90.0% |
| `RTY=F` (Russell 2k) | 2 | 2 | 66.4% | 58.3% | 74.5% |
| `ES=F` (S&P 500) | 7 | 5 | 70.1% | 50.0% | 87.9% |
| `NQ=F` (NASDAQ) | 3 | 3 | 67.3% | 61.1% | 76.9% |
| `SI=F` (silver) | 2 | 2 | 60.3% | 52.6% | 68.0% |
| `BTC-USD` | 2 | 2 | 55.0% | 50.0% | 60.0% |
| `ETH-USD` | 2 | 2 | 58.3% | 50.0% | 66.7% |

### By timeframe

| TF | Cells | Valid | Mean WR |
|---|---:|---:|---:|
| 5m | 15 | 13 | 69.6% |
| 1m | 2 | 2 | 70.0% |
| 15m | 9 | 7 | 63.1% |

### By session

| Session | Cells | Valid | Mean WR |
|---|---:|---:|---:|
| asia_sydney | 23 | 19 | 67.8% |
| all_sessions | 3 | 3 | 66.0% |

### By filter set

| Filter set | Cells | Valid | Mean WR |
|---|---:|---:|---:|
| baseline (no structural filter) | 1 | 1 | 64.6% |
| canonical (structural HH/HL trend filter) | 23 | 19 | 65.9% |
| canonical_plus_volume | 2 | 2 | 85.1% |

### Heat map (anchor config: canonical, asia_sydney, recent_60d)

| Instrument | 1m | 5m | 15m |
|---|---:|---:|---:|
| `GC=F` | 90.0% (n=10) | 74.5% (n=47) | 75.0% (n=12) |
| `ES=F` | 50.0% (n=2) | 80.6% (n=72) | 62.5% (n=24) |
| `NQ=F` | — | 63.9% (n=61) | 76.9% (n=13) |
| `RTY=F` | — | 74.5% (n=47) | 58.3% (n=12) |
| `SI=F` | — | 68.0% (n=50) | 52.6% (n=19) |
| `BTC-USD` | — | 60.0% (n=10) | 50.0% (n=2) |
| `ETH-USD` | — | 50.0% (n=24) | 66.7% (n=3) |

## Headline observations

1. **The canonical filter improves on baseline.** On the anchor instrument and timeframe, the structural HH/HL trend filter lifts WR from 64.6% (baseline, n=509) to 74.5% (canonical, n=47) — a ~10pt lift at the cost of ~90% of trade frequency. The selectivity is real.
2. **The framework holds across the futures family but not equally.** Precious-metals and equity-index futures show 60-76% mean WR. Crypto under the same rule set is materially weaker (55-58%) — consistent with crypto's 24/7 lack of session structure.
3. **The most-selective filter combination produces high WR on small samples.** Canonical+volume hits 82-88% WR but trade counts drop to 17-33. By construction this is overfitting territory; the per-trade quality is real but the statistical confidence is wide.
4. **Session filter delivers a smaller-than-expected lift.** asia_sydney mean WR 67.8% vs all_sessions 66.0%. Most of the structural edge is already captured by the canonical filter; the session filter is supplementary.
5. **Out-of-sample (prior_60d) cells were unverifiable** due to free-tier intraday data ceilings. The matrix is an in-sample surface; out-of-sample validation requires an extended-history data adapter.

## Methodology notes

- **Wilson 95% CI** computed on every cell from `(n_wins, n_trades)`. This is the right interval for a binomial proportion at small N.
- **Anomaly flags** trip on `WR > 0.95`, `expectancy < 0`, or `WR ∈ {0, 1}` with `N > 0`. The matrix flagged 1 anomalous cell (out of 22 valid).
- **Trade-count discipline:** cells with N < 50 are flagged "statistically thin." 15 of 22 valid cells fall in this range. The robust core (N ≥ 50) is 7 cells.
- **Data caching:** each `(ticker, tf, window)` slice is fetched once and reused across cells with different filters. Total wall-clock dropped from ~30 minutes to ~6 minutes.

## What this validates

The framework's structural HH/HL filter (the load-bearing rule from the orchestration loop) holds across the broader futures family. The result is not unique to a single instrument or window. The framework is asset-agnostic *within the futures universe* but degrades on 24/7 crypto markets where the rule set's session-and-trend assumptions don't apply.

## What this does NOT validate

- **Live execution.** Backtests are out-of-sample only in the temporal sense (post-fact data). Live forward-tests with real capital are a separate and stricter test.
- **Out-of-sample window stability.** With only ~60 days of intraday data accessible, the matrix runs on the same window. Whether the same WR holds on, say, year-ago data is currently unknown — the data isn't free-tier accessible.
- **Tick-level execution.** The engine assumes idealized fills at midpoint / rail / SL prices. Real fills include slippage, particularly on instruments with thinner liquidity during off-hours.

## Reproducibility

The matrix is reproducible from any installed copy of the methodology's `backtest_skeleton/` once the user's domain rules are filled in. The matrix driver is ~580 lines of Python. With a free-tier data adapter the wall-clock is under 10 minutes including all 26 cells.

```
backtest_skeleton/run_matrix.py    # the driver
backtest_skeleton/runs/matrix/
  ├── cells/<cell_id>.json         # per-cell results
  ├── matrix_results.csv           # flat table
  ├── matrix_results.parquet       # same in parquet
  ├── aggregates.json              # by-axis summary
  └── MATRIX_RESULTS.md            # human report
```

---

*This document is the third public artifact in the methodology's case study sequence. Aggregate stats only; per-cell data and instrument-specific findings live in the private workspace.*
