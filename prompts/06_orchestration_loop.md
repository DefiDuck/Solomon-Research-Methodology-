# Prompt 6 — Find→Review→Find→Review orchestration loop

**Copy everything below this line into Claude Code.**

---

You are running a multi-agent backtest orchestration loop. The Phase 1 engine (built in Prompt 5) established a baseline metric on the validated rules. {ENTITY}'s verbatim claim is some target metric. The gap between baseline and target is what this prompt closes by systematically sweeping candidate filter conditions.

**Target:** lift baseline by enough to land within 5 pts of {ENTITY}'s number. If achieved, the framework is fully validated by external measurement using only publicly-derivable filters. If not, the residual gap quantifies what's living in non-recoverable channels (e.g. private DMs, real-time pattern recognition, the source's tacit skill that resists encoding).

**You are in the project root.** Read these files first:

1. `findings/KEY_FINDINGS.md` — all Findings, especially the gap Finding
2. `findings/RULE_SET.md` — the verbatim rule set
3. `findings/Findings_Audit.md` — your trust audit
4. `engine/runs/PHASE_1_SUMMARY.md` — the baseline you're trying to beat
5. `engine/solomon_engine/` — engine source you'll be calling

After absorbing context, run the loop below.

---

## The orchestration loop — three roles

You play all three roles yourself in sequence. No Task subagents required (the engine is fast enough that one orchestrator iterating is the right pattern).

### Role 1 — Experimenter

Maintains the experiment queue. Proposes ONE configuration to test per iteration. Priority ranking (test in this order, highest first):

| Rank | Filter | Hypothesis source | Expected lift |
|---|---|---|---|
| 1 | Structural higher-context filter (pattern detection, NOT statistical-trend slope) | Higher-context Finding | +2 to +5 pts |
| 2 | Density / activity threshold at the entry unit | Density Finding | +1 to +3 pts |
| 3 | Freshness filter (only act on structures where the originating event is within last N units) | State Finding | +2 to +4 pts |
| 4 | Time-of-day / phase exclusion (excludes a sub-window where the source rule explicitly does not apply) | Phase Finding | +1 to +3 pts |
| 5 | Asset / instance extension (test the same rule set on adjacent {ASSET}s) | Asset-agnostic Finding | per-asset baseline |
| 6 | Combinations of any of the above that worked individually | composition test | additive |

**Don't test:** any filter for which you lack data at the required resolution. Note as "deferred to extended-data integration."

**Skip if redundant:** don't test combinations that are obviously dominated.

After each filter is decided, the Experimenter proposes the next config based on what's been learned. Use a stack-it-up approach: take the best config so far, add ONE filter, retest. If improved, the new config becomes the best; if not, drop the filter and try the next.

### Role 2 — Backtester

Runs the engine with the proposed config. Implementation:

1. Generate a temp config with the filter parameters.
2. Call `run_backtest()` from your engine with those parameters.
3. Save the result to `engine/runs/orchestration_iter_NN/`.
4. Return the aggregate metrics.

If the engine doesn't already support a filter type, **extend the engine first**, then run the backtest. Engine extensions go in the appropriate module. Test extensions with the Phase 1 baseline first to confirm they don't break existing behavior.

### Role 3 — Analyst

Reviews each iteration's result against the prior best:

**Keep the filter if:**
- Hit-rate improvement ≥ +1 pt, AND
- Expectancy improvement ≥ +0.5 units, AND
- Event count remains ≥ 50 (don't accept overfitting that collapses sample size)

**Drop the filter if:**
- Hit rate or expectancy regresses, OR
- Event count falls below 50

**Mark inconclusive if:**
- Event count is 50–100 AND improvement is +0 to +1 pt (could be noise)
- In this case, run again with a different parameter setting before deciding

Update the running best config after each decision. Maintain a clear log:

```
Iteration NN | filter: <name> | params: <values> | events: N | hit-rate: X% | expect: +Y units | decision: KEEP/DROP/INCONCLUSIVE | new best: Z%
```

### Loop termination

Stop when ANY of these:

1. **Target hit:** best hit-rate within 5 pts of {ENTITY}'s claim. Frame as success.
2. **All single filters tested + best 2-3 combinations tested:** if no further single addition lifts hit rate by ≥1 pt, stop.
3. **Iteration cap:** 20 iterations max.
4. **Event-count collapse:** if every remaining candidate would push event count below 50, stop.

When stopping, write the final summary.

---

## Deliverable

`engine/runs/PHASE_2_SUMMARY.md`. Format:

```
# Phase 2 Orchestration Loop Summary
Date: YYYY-MM-DD
Total iterations: N (of 20 cap)
Total compute time: XX min
Engine extensions added: [list]

## Final score
- Baseline (Phase 1): X.X% / +Y.Y units / Z events
- Final best config: X.X% / +Y.Y units / Z events
- Δ to {ENTITY}'s claim: N pts (was M pts at baseline)
- Status: [TARGET HIT / PARTIAL / NO IMPROVEMENT]

## Final best configuration

## Per-filter results table

## Iteration log

## Findings status updates

## Recommendations for next phase
```

---

## Important rules

- **Use the engine's data cache.** Once data for the test window is fetched, all iterations reuse it.
- **Backwards compatibility:** any engine extension must NOT break the Phase 1 baseline reproduction. Test by re-running the original config — should produce same metrics exactly.
- **Honest about overfitting:** if the final best config has only 60–100 events, flag this. Lower count = higher overfitting risk.
- **No real-world actions.** Backtest only.
- **If you discover a contradiction with an existing Finding, flag it.**
- **Time budget:** ~90–120 min total.

When complete, summarize the gap-closing result. Tell the user whether you hit the target, partially closed, or stalled. Recommend the next phase.

---

## What this enables (context)

- **If target hit:** the framework is empirically validated using only publicly-derivable rules. The book / spec becomes deployable, not theoretical.
- **If partial close:** strong validation, residual gap is likely the non-recoverable layer.
- **If no improvement:** baseline rules are the whole rule set. Any further edge requires real-time pattern recognition or filter conditions you haven't identified yet.

Either way, this prompt produces the **score**.
