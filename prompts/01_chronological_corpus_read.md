# Prompt 1 — Full chronological read of {CHANNEL_PRIMARY} (parallel subagents)

**Copy everything below this line into Claude Code.**

---

You are working on a long-running reverse-engineering investigation of {ENTITY}'s tacit {RULE_NAME} method. {ENTITY} is the source whose practice you are decoding; {STUDENT} is the investigator. There are approximately N total messages in `{CORPUS_FILE_A}`, of which M are from {ENTITY}, spanning roughly {DATE_RANGE_START} through {DATE_RANGE_END}.

**You are in the project root.** Read these files first to absorb full context (in this order):
1. `README.md` — current state of investigation
2. `analysis/Facts_Log.md` — verbatim quotes already cataloged (do NOT re-extract these)
3. `findings/KEY_FINDINGS.md` — all current Findings, each graded FACT / HYPOTHESIS / SPECULATION
4. `findings/RULE_SET.md` — the current portable rule set
5. `findings/OPEN_QUESTIONS.md` — current test queue

After absorbing context, your job is to find every {RULE_NAME}-relevant {ENTITY} message in `{CHANNEL_PRIMARY}` that is **NOT already in the Facts Log**. The Facts Log is comprehensive for keyword-mined material; what we are missing is **conversational context, themes that don't surface from keyword search, and substance buried in long exchanges**.

## Method — parallel subagents

Spawn `K` Explore subagents (1 per date range), where K is large enough that no single subagent reads more than ~600 source messages. For example, for a 2-year corpus split by quarter:

| Agent | Date range | Approx {ENTITY} msg count |
|---|---|---|
| A | {Q1_RANGE} | ~600 |
| B | {Q2_RANGE} | ~700 |
| ... | ... | ... |

Each subagent gets the same brief: "Read every {ENTITY} message in this date range from `{CORPUS_FILE_A}`. Return verbatim quotes (with timestamps) for any message that is {RULE_NAME}-relevant. Categories of interest: {DOMAIN}-method or concept references, structure / pattern / primitive references, time / sequence / exit references, state classification (steady / changing) references, multi-context / multi-resolution references, scope / window / phase references, risk discipline, performance claims (hit rate, ROI, etc.), anything cryptic or analogical, anything {ENTITY} flags as a hint or secret, any direct teaching to {STUDENT}. Skip social chat, gaming, food, life-talk **unless** it contains a {DOMAIN} metaphor. Do NOT re-extract quotes already present in `analysis/Facts_Log.md`. Return up to 100 candidates with brief 1-line context for each."

## Synthesis (you, the orchestrator)

After all subagents return:
1. De-duplicate against the existing Facts Log.
2. Group new quotes thematically (e.g. by primitive type, exit type, sub-window, performance, meta).
3. Flag any quote that contradicts an existing Finding.
4. Flag any quote that strongly corroborates a current HYPOTHESIS (eligible to promote to FACT).
5. Identify any new theme that warrants a new Finding.

## Deliverable

Write the result to: `prompt_results/01_corpus_full_read_RESULT.md` (create the folder if needed).

Format:
```
# Corpus Full Chronological Read — Result
Date: [YYYY-MM-DD]
Subagents run: K
New quotes found: N
New themes identified: M
Findings to promote: [list]
Findings to revise: [list]

## Section 1 — New verbatim quotes by theme
[grouped quotes with timestamps and 1-line context]

## Section 2 — Corroborations of existing Findings
[quote → existing Finding ID → effect]

## Section 3 — Contradictions to existing Findings
[quote → existing Finding ID → what changes]

## Section 4 — Proposed new Findings
[Finding draft, status FACT/HYPOTHESIS, source quotes]

## Section 5 — Themes worth deeper investigation
[short list of follow-up questions]
```

## Important rules
- Verbatim only. No paraphrasing. Preserve typos, formatting, emoji.
- Every claim has a timestamp and exact quote. No claims without sources.
- Skip everything in `archive/` directories — those are old grep dumps.
- Skip everything that is unrelated meta-tooling (e.g. tool docs, third-party READMEs).
- Time budget: aim for ~90 min total. If a subagent is taking too long on social chat, instruct it to skip ahead.
- Cost discipline: cap each subagent at ~20k tokens of returned content. **The orchestrator does the synthesis, not the subagents.**

When complete, summarize the result file's contents in a single paragraph and ask the user whether to integrate it into the canonical docs.
