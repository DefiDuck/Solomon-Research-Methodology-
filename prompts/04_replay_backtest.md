# Prompt 4 — Per-instance replay backtest of every {ENTITY}-claimed event

**Copy everything below this line into Claude Code.**

---

You are continuing the {RULE_NAME} reverse-engineering. This prompt is the **highest-value validation step** in the investigation: replay every {ENTITY}-posted artifact against ground-truth historical data, measuring whether the rules in `findings/RULE_SET.md` produce the outcomes {ENTITY} claimed.

**Critical:** This prompt requires either (a) a Claude Code session with a programmatic ground-truth-data adapter (browser MCP, API client, or local data store), OR (b) a human-in-the-loop where the user drives the replay and the agent records observations. Pick one mode in Step 1.

**You are in the project root.** Read these files first:
1. `findings/RULE_SET.md` — the rule set you're testing
2. `findings/KEY_FINDINGS.md` (esp. {ENTRY_RULE}, {EXIT_RULE}, {SIGNAL_FEATURE} validation, {WINDOW}-edge claims)
3. `prompt_results/03_visual_evidence_table_RESULT.md` — the master artifact table from Prompt 3 (run that first)

If the visual evidence table from Prompt 3 doesn't exist yet, **stop and tell the user to run Prompt 3 first.** This prompt depends on it for per-event timestamp / instance / feature data.

## Method

### Step 1 — Mode selection

Ask the user: "Do you want me to drive the replay programmatically (autonomous), or do you want to drive while I record observations (interactive)? For autonomous mode, the data adapter (e.g. browser MCP) must be connected and your replay surface must allow programmatic interaction. For interactive mode, I'll guide you step-by-step."

### Step 2 — Build the test queue

From the visual evidence table, filter for rows where:
- timestamp is identifiable to within {SUFFICIENT_PRECISION}
- {ASSET} is one for which ground-truth historical data is available
- timestamp is within the data adapter's effective replay window (some adapters cap at N days for fine resolutions)
- The artifact shows a {RULE_NAME}-claimed entry ({ACTIVE_PAIR} + {ENTRY_RULE} mark visible)

Skip rows that don't meet all 4. Expected queue size: 15–25 events.

### Step 3 — For each event in the queue

Sequential or parallel (one subagent per event). Each event test:

1. **Open the replay surface**, navigate to the {ASSET}, set resolution to match the artifact.
2. **Replay to the timestamp** (~5 {GRANULARITY} units before entry).
3. **Measure entry-time {SIGNAL_FEATURE}s:** identify the {ACTIVE_PAIR} at entry-T0. Compute the {MIDPOINT}.
4. **Compare to artifact:** does our computed {MIDPOINT} match the artifact's apparent entry value within tolerance?
5. **Step replay forward unit-by-unit** from entry. For each unit, record:
   - unit index (1, 2, 3, ...)
   - high, low, close (or domain-equivalent extremes)
   - max favorable excursion so far
   - max adverse excursion so far
6. **Stop measuring when one of:**
   - Unit 20 is reached (cap to keep runs bounded)
   - 1:1 RR target is exceeded (claim TP achieved this unit)
   - Opposite-rail SL is hit
   - {ENTITY}'s caption (if known from corpus context) indicates exit
7. **Record per-event row:**
   - {ASSET}, {GRANULARITY}, timestamp, {MIDPOINT} computed, midpoint matched? (Y/N), units to TP, units to SL, MAE, MFE, time-stop equivalent (= median units to TP across the queue, computed at end)

### Step 4 — Aggregate analysis

After all events tested, compute:

- **Hit rate** (proportion that hit 1:1 TP before opposite-rail SL): tests {ENTRY_RULE} + RR claim
- **Median units to TP** at each {GRANULARITY}: this is the empirical N for {EXIT_RULE}
- **Median MFE / MAE ratio**: tests the "no adverse excursion" claim if {ENTITY} made one
- **Midpoint match rate** (% within tolerance): tests {ENTRY_RULE} generalization

Identify the **single most informative event** — the one where {EXIT_RULE} is most clearly derivable. Recommend an N for the {TIME_STOP_N} forward-test going forward.

## Deliverable

Write the result to: `prompt_results/04_replay_backtest_RESULT.md`.

Format:
```
# Replay Backtest — Result
Date: [YYYY-MM-DD]
Mode: [autonomous / interactive]
Events in queue: N
Events successfully replayed: M
Events skipped (data unavailable / unreadable): N-M

## Section 1 — Aggregate results
- Hit rate: X%
- Median units to TP, by {GRANULARITY}: {...}
- Median MFE / MAE ratio: X
- {MIDPOINT} match rate (within tolerance): Y%
- Recommended {TIME_STOP_N} for next forward-test: {...}

## Section 2 — Per-event results
[one row per replayed event]

## Section 3 — Findings status updates

## Section 4 — Specific events worth surfacing
- Event with cleanest {EXIT_RULE} derivation: [details]
- Event that contradicts current rule set: [details]
- Event where {ENTITY}'s outcome (per their caption) matched our reproduction: [details]
```

## Important rules

- **Do not actually execute any real-world action.** This is replay only.
- Some replay surfaces have free-tier session limits. If hit, stop, tell the user, resume tomorrow.
- For each event, capture a snapshot at entry-T0 and at exit, save to `tests/replay_screenshots/replay_NNN_<asset>_<date>.png`.
- Time budget: ~5 min per event interactive, ~3 min per event autonomous.
- If an event can't be replayed (data unavailable), record the reason and move on. Don't get stuck.

When complete, summarize and ask the user whether to integrate the findings.
