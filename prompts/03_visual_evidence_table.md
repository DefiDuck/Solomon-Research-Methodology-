# Prompt 3 — Visual analysis of every {ENTITY}-posted artifact (parallel subagents)

**Copy everything below this line into Claude Code.**

---

You are continuing the {RULE_NAME} reverse-engineering. {ENTITY} has posted ~N artifacts (images / screenshots / charts / diagrams) across {CHANNEL_PRIMARY} and {CHANNEL_SECONDARY}. We need a systematic visual evidence table — one row per artifact — that tests our current rule set against every image.

**You are in the project root.** Read these files first:
1. `findings/RULE_SET.md` — the rule set you'll be testing each artifact against
2. `findings/KEY_FINDINGS.md` (esp. the highest-confidence Findings)
3. `analysis/Facts_Log.md` (the sections discussing the most-referenced artifacts)

## The artifacts to analyze

Folders (counts approximate):
- `source_material/visual_archive/{CHANNEL_PRIMARY}_curated/` — {ENTITY}'s self-curated examples
- `source_material/visual_archive/{CHANNEL_PRIMARY}_additional/` — supporting context
- `source_material/visual_archive/{CHANNEL_SECONDARY}/` — 1-on-1 share-outs

## Method — parallel subagents

Spawn ~5 Explore subagents with the Read tool (vision-capable). Split by folder and approximate filename ranges so each agent reads ~10–30 artifacts.

Each subagent's brief: "Read each image in your assigned folder using the Read tool. For each image, extract a structured row with the following fields:

- **filename**
- **subject / instance** (the specific {ASSET} the artifact references)
- **{GRANULARITY}** (the resolution / scope visible in the artifact)
- **timestamp range visible** (any date axis or visible labels)
- **current state value** (the latest measurement visible)
- **{SIGNAL_FEATURE}s visible** (list each one + any color/stylistic encoding)
- **{ACTIVE_PAIR} (if identifiable)** — the two features bounding the current state
- **{MIDPOINT} of {ACTIVE_PAIR}** (computed)
- **{ENTRY_RULE} mark visible** (yes/no, the value if yes)
- **{ENTRY_RULE}={MIDPOINT} test** (PASS / FAIL / UNCLEAR — entry must be within the documented tolerance of the midpoint)
- **primitive-validation count** (how many distinct supporting events does the artifact show for each {SIGNAL_FEATURE}?)
- **time-window visible** (how many {GRANULARITY} units are shown end-to-end?)
- **sub-window markers visible** (if the artifact overlays {WINDOW_A}/{WINDOW_B} categories)
- **annotations** (hand-drawn marks, arrows, text)
- **corpus context anchor** (filename or timestamp linking back to the surrounding corpus discussion)

For artifacts that include encoded layers (e.g. dashed lines, color-coded regions), also note the encoding meaning if it's documented in any Finding."

## Synthesis (you, the orchestrator)

After all subagents return:
1. Build a master CSV/markdown table with all rows.
2. Run aggregate stats:
   - **{ENTRY_RULE}={MIDPOINT} pass rate** (Finding-1 falsifier: failed if <60% across N=10+ {RULE_NAME}-labeled artifacts).
   - **Average time-window visible** (operationalizes the {TIME_STOP_N} hypothesis).
   - **Distribution of {GRANULARITY} used.**
   - **Distribution of {ASSET} type.**
   - **Distribution of {WINDOW} at the entry timestamp.**

3. Identify any artifact that contradicts a Finding.
4. Identify the single artifact that gives the cleanest evidence for the {EXIT_RULE} — i.e. one where you can count exactly the time-window from entry to a visible exit.

## Deliverable

Write the result to: `prompt_results/03_visual_evidence_table_RESULT.md`.

Format:
```
# Visual Evidence Table — Result
Date: [YYYY-MM-DD]
Total artifacts analyzed: N
{ENTRY_RULE}={MIDPOINT} PASS rate: X% (n_pass / n_testable)
Average time-window visible: X (n=Y)
{GRANULARITY} distribution: {...}
{ASSET} distribution: {...}
{WINDOW}-at-entry distribution: {...}

## Section 1 — Master table
[row per artifact]

## Section 2 — Findings status updates

## Section 3 — Notable artifacts
- Cleanest {EXIT_RULE} evidence: [filename] (N units from entry to exit)
- Cleanest {ENTRY_RULE}={MIDPOINT}: [filename]
- Any contradictions to current rule set: [list]
```

## Important rules
- Read each image with the Read tool. Don't guess from filename.
- If an image is unreadable or not relevant (e.g. a meme), record "non-{ASSET}" and skip its evidence row.
- {MIDPOINT} computation: (upper + lower) / 2. Use the precision the artifact actually shows.
- Cap each subagent at ~10k returned tokens.

When complete, summarize and ask the user whether to integrate.
