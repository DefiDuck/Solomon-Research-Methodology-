# Prompt 5 — Build the Python backtest engine + Phase 1 validation runs

**Copy everything below this line into Claude Code.**

---

You are building the long-term backtest infrastructure for the {RULE_NAME} reverse-engineering. Driving the replay surface event-by-event is the wrong tool for testing rules at scale. A reproducible Python pipeline is the right one. This prompt builds that pipeline, then immediately uses it to test the most measurable Findings.

**You are in the project root.** Read these files first:

1. `README.md` — current state of investigation
2. `findings/KEY_FINDINGS.md` — all current Findings with status (FACT / HYPOTHESIS / SPECULATION)
3. `findings/RULE_SET.md` — the rule set you're implementing in code
4. `findings/Findings_Audit.md` — your trust audit
5. `findings/OPEN_QUESTIONS.md` — the test queue
6. `prompt_results/03_visual_evidence_table_RESULT.md` — quantitative N values per {GRANULARITY}

After absorbing context, do the following.

---

## Phase 1 — Build the engine

Create a new directory `engine/` with this structure:

```
engine/
├── README.md
├── requirements.txt
├── solomon_engine/
│   ├── __init__.py
│   ├── data.py              ← ground-truth fetching with cache (default + optional adapter)
│   ├── primitives.py        ← {SIGNAL_FEATURE} validation per the documented primitive rule
│   ├── state.py             ← state classification per the documented state rule
│   ├── selector.py          ← {ACTIVE_PAIR} + {MIDPOINT} detection
│   ├── simulate.py          ← per-event simulation with {EXIT_RULE} primary + boundary backstop
│   ├── backtest.py          ← top-level run loop
│   └── report.py            ← per-event table + aggregate metrics
├── runs/
└── cli.py
```

### Engine API contract

These functions are the contract. The rest of the modules support them.

```python
# data.py
def fetch_data(asset: str, granularity: str, start: str, end: str, source: str = "default") -> pd.DataFrame:
    """Returns columns: timestamp, plus the per-domain measurements you need.
    granularity in your set of allowed values.
    The default source has limits — document them. An optional adapter (with API key
    in env) extends history."""

# primitives.py
def find_validated_primitives(df: pd.DataFrame, lookback: int, tolerance: float, ...) -> List[Primitive]:
    """Per your primitive-validation rule (e.g. N same-type touches). Returns
    Primitive(value, type, n_supports, first_idx, last_idx)."""

# state.py
def classify_state(df: pd.DataFrame, idx: int, lookback: int) -> str:
    """Per your state rule. Returns one of {STATE_VALUES}."""

# selector.py
def find_active_pair(value: float, primitives: List[Primitive]) -> Tuple[Primitive, Primitive]:
    """Returns (lower, upper) — the two adjacent primitives bounding `value`.
    None if `value` is outside all primitives."""

def midpoint(pair: Tuple[Primitive, Primitive]) -> float:
    return (pair[0].value + pair[1].value) / 2.0

# simulate.py
@dataclass
class Event:
    entry_idx: int
    entry_value: float
    direction: int  # +1 long-equivalent, -1 short-equivalent
    sl_value: float
    time_stop_n: int  # {TIME_STOP_N}: domain-scaled
    exit_idx: int = None
    exit_value: float = None
    exit_reason: str = None  # 'time' | 'sl' | 'tp_1r' | 'end_of_data'
    mfe_units: float = 0
    mae_units: float = 0

def simulate_event(df: pd.DataFrame, event: Event, unit_size: float) -> Event:
    """Walk forward unit-by-unit from entry_idx. Update mfe/mae each unit.
    Exit when: (a) time_stop_n units elapsed, (b) sl_value crossed, (c) +1R reached."""

# backtest.py
def run_backtest(
    asset: str,
    granularity: str,
    start: str,
    end: str,
    entry_rule: str = "midpoint",      # or "rail_lower" / "rail_upper" / etc.
    time_stop_n: int = None,           # if None, use {GRANULARITY} default
    state_filter: str = "any",
    window_filter: List[str] = None,
    source: str = "default",
) -> BacktestResult:
    """Main loop:
    1. Fetch data.
    2. Walk through every unit.
    3. At each unit: classify state, find active pair, check entry rule.
    4. If entry rule fires: simulate event, append to results.
    5. Return BacktestResult with per-event list + aggregate metrics."""

# report.py
def write_report(result: BacktestResult, run_id: str) -> Path:
    """Write per-event CSV + aggregate JSON + human-readable markdown."""
```

### Implementation notes

- **Unit sizes:** ticker-keyed dict for whatever your domain uses (price tick, character count, time unit, etc.).
- **Sub-windows:** documented start/end times for each named window. Use `datetime.time` for filtering if temporal.
- **Default {ENTRY_RULE}:** {MIDPOINT} of {ACTIVE_PAIR}, with rail-entry alternatives that the orchestration loop can sweep.
- **Hit-rate target:** match {ENTITY}'s claimed metric (per your highest-trust Finding on performance).
- **Don't over-engineer:** plain pandas DataFrames, no fancy event-loop. The simplest possible correct implementation. Speed isn't the bottleneck; reproducibility is.

---

## Phase 2 — Initial validation runs

Once the engine is functional, run validation backtests. Each tests a specific Finding. Save each result to `engine/runs/validation_NN_<finding>/`.

### Run 1 — {ENTRY_RULE} test
- Pick the highest-density {ASSET} you have ground-truth data for, on its primary {GRANULARITY}, over the longest window the data adapter supports.
- entry_rule "midpoint", time_stop_n at the documented default.
- Expected: ≥60% hit rate at 1:1 if {ENTRY_RULE} holds.
- Falsification: <50% hit rate.

### Run 2 — Rail-entry alternative
- Same parameters but entry_rule "rail_lower" / "rail_upper".
- Should give similar or higher hit rate if rail-entry is also valid.

### Run 3 — Higher-context filter
- Add a higher-{GRANULARITY} state-direction filter.
- Compare hit rate against Run 1.
- If Run 3 > Run 1 by ≥5 pts, the higher-context filter is real edge.

### Run 4 — {TIME_STOP_N} sweep
- Run with time_stop_n in a sweep set (e.g. {5, 8, 10, 12, 15, 20, 25, 30}).
- Plot hit rate vs N, expectancy vs N. Pick the N that maximizes expectancy.

### Run 5 — Macro filter
- If you have a macro-level Finding, identify its events on the higher granularity over the past 12 months.
- For each event, run the standard backtest on the lower granularity for the next 24 hours (or domain-equivalent window).
- Compare hit rate inside-the-macro-event vs outside-it.
- If inside > outside by ≥10 pts, macro-filter hypothesis supported. If equal, retire.

### Aggregate deliverable

Write `engine/runs/PHASE_1_SUMMARY.md` with:
- Findings status updates
- Per-run details with links
- Surprises
- Next questions

---

## Important rules

- **Use the default data source** unless you have a specific reason for the optional adapter.
- **Don't take real-world actions or move money or any equivalent.** Backtest only.
- **Verbatim correctness over speed.** Implement the rules as documented, not as you intuit they should be.
- **Save all data fetched** to a cache directory so subsequent runs don't re-hit the API.
- **If a fetch fails, report and skip.** Don't get stuck retrying.
- **Time budget:** ~90 min total. Engine build ~45 min, validation runs ~30 min, summary ~15 min.

When complete, summarize Phase 1 results and ask whether to proceed to Phase 2 (orchestration loop) or integrate findings first.

---

## What this enables (context for Prompts 6, 7, 8)

- **Prompt 6:** Find→Review→Find→Review orchestration loop. Sweep filter conditions until convergence. Uses this engine.
- **Prompt 7:** Live event receiver. Capture {ENTITY}-fired live signals to grow your sample beyond the historical corpus.
- **Prompt 8:** Compare backtest results to {ENTITY}'s verbatim claimed metric. If our engine gets within 5 points of their number using only documented rules, the framework is fully validated by external measurement.

This prompt is the foundation. Build it solid.
