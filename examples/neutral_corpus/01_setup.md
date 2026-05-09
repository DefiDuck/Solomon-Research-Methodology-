# Setup — instantiating the methodology for a code-review corpus

Concrete steps to go from "pick a project" to "ready to run prompt 01."

## Step 1 — Pick a project

A reasonable filter:

- ≥3 years of public PR activity
- ≥500 closed PRs
- One primary maintainer who handles ≥60% of merge decisions
- Public review comments on most PRs
- A `CONTRIBUTING.md` to establish the *articulated* rule baseline

Document the choice in `README.md` of your investigation directory. Don't move on until the choice is recorded — the audit chain starts there.

## Step 2 — Export the corpora

Two corpora, similar to {CORPUS_A} and {CORPUS_B} in the methodology:

### {CORPUS_A} — PR comments and decisions

Export every PR closed in the last N years. For each PR, capture:

- PR number, title, author, created_at, closed_at, merged (bool)
- Files changed (paths only, not content)
- Each review comment by the maintainer: comment_id, body, created_at, in_reply_to
- The final outcome (merged / closed-without-merge)

Suggested format: JSONL, one PR per line.

This is the high-volume corpus. The maintainer might leave hundreds of comments per month here.

### {CORPUS_B} — mailing list / forum / chat archives

Lower-volume but often higher-trust because the maintainer might explain reasoning more thoroughly when not constrained by GitHub's PR UI.

Export every thread the maintainer participated in over the same window. Per thread:

- Thread ID, subject, started_at
- Each maintainer message: timestamp, body, in_reply_to

## Step 3 — Set up the directory

```
my_investigation/
├── README.md
├── 01_source/
│   ├── prs.jsonl          ← {CORPUS_FILE_A}
│   └── mailing_list.mbox  ← {CORPUS_FILE_B}
├── 02_analysis/
│   └── Facts_Log.md       (empty, populated by Prompt 1)
├── 04_findings/
│   ├── KEY_FINDINGS.md    (starts with the CONTRIBUTING.md as baseline)
│   ├── Findings_Audit.md  (empty)
│   ├── RULE_SET.md        (empty, populated by Prompt 5)
│   └── OPEN_QUESTIONS.md  (starts with your research questions)
├── 06_prompts/
│   └── (copy from public-methodology/prompts/, with placeholders substituted)
├── 08_engine/
│   └── (copy from public-methodology/backtest_skeleton/, with TODOs filled)
└── tests/
    └── (held-out PRs, used in Phase 2)
```

## Step 4 — Substitute placeholders in the prompts

Open each prompt under `06_prompts/`. Find every `{PLACEHOLDER}` and replace with your specifics. The mapping from `examples/neutral_corpus/00_overview.md` covers all the standard placeholders.

Tip: do this with a single sed/Python script so you can re-do it cleanly if you change projects.

## Step 5 — Define the backtest target

Before running any prompts, write down — in a single file — what you're trying to measure:

```
Target: predict the maintainer's accept/reject decision for held-out PRs.
Metric: % accuracy on N=100 held-out PRs.
Baseline: a simple rule "if it has tests AND author is regular contributor, accept." Measure this baseline first.
Stretch: rule set extracted by Prompts 1-6 should beat the baseline by ≥10 pts.
```

Without this written down, Phase 2 is a moving target. Write it before you start.

## Step 6 — Define the held-out test set

Pick 100 PRs that are **NOT** going into the training corpus. Record their PR numbers in a separate file. The backtest will only see these at the end.

Discipline: don't peek. The held-out set is invisible to Prompts 1-6 and only appears in Prompt 8 as the calibration sample.

## Step 7 — Define the FACT criteria for this domain

A maintainer-quote becomes FACT-grade if:

- The quote appears in ≥1 PR review by the maintainer (not in a third-party comment).
- The quote is a direct statement (not a question, not sarcasm).
- The quote can be verified by opening the PR.

A pattern becomes HYPOTHESIS-grade if:

- It's a generalization across ≥10 PRs.
- The falsification rule is "find ≥3 PRs that contradict the pattern." (3 = enough to falsify a claimed near-universal rule, but not so few that one-off exceptions kill it.)

A SPECULATION:

- Anything else the investigator notices.

These FACT/HYPOTHESIS/SPECULATION rules are domain-specific. Write them down so future audits use the same criteria. The Solomon-method discipline applies; the *thresholds* are yours to set.

## Step 8 — Optional: pre-register

For maximal rigor (e.g. if the result might be published or used in a public claim), pre-register the investigation:

- The project chosen.
- The held-out PR list.
- The baseline metric.
- The stretch metric.
- The expected timeline.

A pre-registered investigation can't be retro-fitted to look successful. The pre-registration is the audit trail.

## Done

You're ready to run Prompt 1. Open Claude Code in the `my_investigation/` directory and paste `06_prompts/01_chronological_corpus_read.md`.
