# Prompt 2 — Full chronological read of {CHANNEL_SECONDARY} (parallel subagents)

**Copy everything below this line into Claude Code.**

---

You are continuing a long-running reverse-engineering investigation of {ENTITY}'s tacit {RULE_NAME} method. {ENTITY} and {STUDENT} have a 1-on-1 conversation in `{CORPUS_FILE_B}`, spanning roughly {DATE_RANGE_START} through {DATE_RANGE_END}, plus N attached artifacts (images / files) in the same folder.

**Why {CHANNEL_SECONDARY} matters more than {CHANNEL_PRIMARY}:** the primary channel was public to other observers, and {ENTITY} has documented in writing that they intentionally post misdirection in public messages. The 1-on-1 secondary channel has no such audience and is therefore higher-trust. **Anything verbatim here outweighs anything in `{CORPUS_FILE_A}`.**

**You are in the project root.** Read these files first:
1. `README.md`
2. `analysis/Facts_Log.md` (esp. the sections covering quotes from `{CHANNEL_SECONDARY}`)
3. `findings/KEY_FINDINGS.md`
4. `findings/RULE_SET.md`

## Method — parallel subagents

Spawn 4 Explore subagents using the Task tool, one per quarter (or finer if the corpus is large):

| Agent | Date range |
|---|---|
| W1 | {Q1_RANGE} |
| W2 | {Q2_RANGE} |
| W3 | {Q3_RANGE} |
| W4 | {Q4_RANGE} |

Each subagent's brief: "Read `{CORPUS_FILE_B}` for messages in this date range. Return verbatim quotes (with timestamps in original format) for any {ENTITY} message that is {RULE_NAME}-relevant. Categories: {DOMAIN}-method or concept, structure / primitive references, sequence / exit, sub-window / scope, state classification, risk discipline, multi-context stack, hit-rate claims, anything cryptic or analogical, any direct teaching to {STUDENT}, any reference to a posted artifact. Skip personal/social chat unless it contains a {DOMAIN} metaphor. Skip {STUDENT}'s messages **unless** they are direct guesses about {RULE_NAME} that {ENTITY} responded to (capture both sides for those). Do NOT re-extract quotes already in the Facts Log sections covering this channel. Return up to 80 candidates."

Additionally, give each subagent this critical secondary task: "Identify the timestamp of every artifact {ENTITY} shared (filename pattern `{ARTIFACT_PATTERN}`). For each artifact, capture the immediately preceding and following ~5 messages of context. Return a per-artifact context table."

## Synthesis (you, the orchestrator)

After all subagents return:
1. De-duplicate against existing Facts Log sections covering this channel.
2. **Verbatim-VERIFY any paraphrase-grade quotes** currently in the Facts Log (mark "paraphrase pending verification"). Replace with exact strings.
3. Cross-reference the artifact context with `{ARTIFACT_FOLDER}/*.{EXT}` filenames so each artifact has an {ENTITY}-quote context anchor.
4. Flag corroborations / contradictions / new themes (same as Prompt 1).

## Deliverable

Write the result to: `prompt_results/02_secondary_corpus_full_read_RESULT.md`.

Format:
```
# Secondary-Corpus Full Chronological Read — Result
Date: [YYYY-MM-DD]
Subagents run: 4
New quotes found: N
Paraphrases verified: [count and verbatim corrections]
Artifact context anchors created: [count]

## Section 1 — Verbatim corrections to Facts Log
[per quote: paraphrase | verbatim | timestamp delta]

## Section 2 — New verbatim {ENTITY} quotes by theme
[grouped quotes with timestamps and 1-line context]

## Section 3 — Artifact context table
[filename | {ENTITY} quote immediately before | {ENTITY} quote immediately after | inferred context]

## Section 4 — Corroborations / contradictions / new findings
```

## Important rules
- Verbatim only. Preserve original format markers exactly.
- Artifact filenames are the link between the corpus text and any visual evidence cataloged in earlier passes. Make sure every artifact has a context anchor.
- Skip files outside `{ARTIFACT_FOLDER}/`.
- Cap each subagent at ~15k tokens returned.

When complete, summarize the result file in one paragraph and ask the user whether to integrate.
