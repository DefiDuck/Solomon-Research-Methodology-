# The 8-prompt sequence

Each `.md` file in this folder is a paste-ready prompt for Claude Code. Run them in order. Each prompt's output enriches the next.

## The placeholder convention

Every prompt uses placeholders. Replace them with your specifics before pasting:

| Placeholder | Meaning |
|---|---|
| `{CORPUS}` | The body of source material. E.g. "all messages from January 2022 through December 2025." |
| `{DOMAIN}` | The field of application. E.g. "code review," "trading," "editorial review." |
| `{ENTITY}` | The source person whose tacit rules you are reverse-engineering. The expert. |
| `{STUDENT}` | The investigator (you, or whoever is being taught by the source). |
| `{RULE_NAME}` | The internal name the source has given their rule set, if any. |
| `{ASSET}` | The specific item the rule set operates on. E.g. "pull requests," "instances of `<event>`." |
| `{CHANNEL_PRIMARY}` | The largest text channel. Usually a public group chat. |
| `{CHANNEL_SECONDARY}` | A smaller, higher-trust 1-on-1 channel. Often where the real teaching happens. |
| `{CORPUS_FILE_A}` | The exported data file for `{CHANNEL_PRIMARY}`. |
| `{CORPUS_FILE_B}` | The exported data file for `{CHANNEL_SECONDARY}`. |
| `{GRANULARITY}` | The temporal resolution of measurements (5min bars, daily summaries, per-PR snapshots, etc.). |
| `{WINDOW_A}, {WINDOW_B}` | Sub-period categories. E.g. timezone sessions, calendar quarters, project phases. |
| `{SIGNAL_FEATURE}` | A primitive feature the rule set operates on. The lowest-level building block. |
| `{ACTIVE_PAIR}` | The two adjacent features bounding the current state. |
| `{MIDPOINT}` | The 50% reference between an active pair. |
| `{ENTRY_RULE}` | A predicate that fires when a tradeable / actionable event occurs. |
| `{EXIT_RULE}` | A predicate that closes the actionable event. |
| `{TIME_STOP_N}` | An exit deadline in {GRANULARITY} units. |
| `{METRIC}` | A measurable outcome the source claims (hit rate, accuracy, ROI, etc.). |

## The 8 prompts

| # | File | Purpose | Inputs | Outputs |
|---|---|---|---|---|
| 1 | `01_chronological_corpus_read.md` | Read `{CHANNEL_PRIMARY}` end-to-end, extract verbatim source quotes that hint at rules. | `{CORPUS_FILE_A}` | A graded list of new quotes. |
| 2 | `02_secondary_corpus_read.md` | Read `{CHANNEL_SECONDARY}` (higher trust). Verify or refine quotes from Prompt 1. | `{CORPUS_FILE_B}` | Verbatim corrections to Prompt 1's output. |
| 3 | `03_visual_evidence_table.md` | If the source posted images / charts / artifacts, build a structured table of every one. | Image folder. | One row per artifact. Match each to a candidate rule. |
| 4 | `04_replay_backtest.md` | Trade-by-trade (or case-by-case) verification of source-claimed outcomes against ground-truth data. | Visual table from Prompt 3. | A measured per-case result. |
| 5 | `05_python_backtest_engine.md` | Build the reusable engine. Encode the documented rules. Run initial validation backtests. | Findings docs + ground-truth data API. | Engine + Phase 1 metrics. |
| 6 | `06_orchestration_loop.md` | Find→Review→Find→Review. Sweep filter conditions until the gap to `{METRIC}` is closed. | Phase 1 baseline + filter candidates. | Phase 2 best config + per-iteration log. |
| 7 | `07_live_event_receiver.md` | Optional — set up live capture of source-fired signals to grow your sample beyond the historical corpus. | Live signal feed. | Append-only event log. |
| 8 | `08_external_calibration.md` | Compare your reverse-engineered metric against the source's verbatim claim. Quantify residual gap. | Phase 2 + live event log. | A single calibration number + provenance. |

**Run order recommendation:** 1 → 2 → 3 → 4 → 5 → 6. Prompt 7 is optional and only valuable after 6. Prompt 8 is the final scoreboard.

## What each prompt produces

Every prompt writes its deliverable into a date-stamped file in a `results/` folder. After each run, integrate the deliverable into your canonical docs:

- New verbatim quotes → your **Facts Log**
- New / corroborated / contradicted claims → your **Findings file**
- New questions raised → your **Open Questions** queue
- Validated rules → your **rule-set spec doc**

Keep canonical docs as the single source of truth. Archive the raw prompt outputs separately.

## Cost discipline

Each prompt is designed to take 30 min – 2 hours of compute. The bulk of the work is parallel sub-reads or sub-image-analyses; the orchestrator does only synthesis.

If a prompt blows past 2 hours of compute or hits output token limits, **stop and chunk it smaller**. The methodology is robust to chunked execution. Don't power through truncations.
