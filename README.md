# The Solomon Method

A reusable methodology for reverse-engineering tacit rules from an expert's recorded communications, then validating those rules against measurable outcomes.

## What this is

A discipline. Not a domain. The Solomon method works on any corpus where someone with a hard-to-articulate practice has left a long trail of communication about that practice — and where their decisions can be backtested against an external ground truth.

**Examples of where this applies:**

- An open-source maintainer's tacit code-review criteria, decoded from years of public PR threads, validated against accept/reject ground truth.
- A senior writer's editorial standards, decoded from their review feedback in a publication's archive, validated against published-vs-rejected outcomes.
- A protocol designer's design philosophy, decoded from their commentary in standards body mailing lists, validated against which proposals shipped.
- A clinician's diagnostic heuristics, decoded from their teaching cases, validated against outcomes (where IRB and privacy permit).

**Core stance:**

You start from the assumption that the expert can't fully articulate their own method. They've described it in fragments, jokes, frustrated corrections, and tangents over years. The corpus contains the method. Your job is to extract it, audit it for the difference between teaching mode and goofing mode, and test what you extracted against measurable outcomes.

## What's in this folder

| Folder | What it contains |
|---|---|
| `/prompts` | Eight reusable prompts you copy-paste into Claude Code (or another agentic CLI) to drive the pipeline. Domain-neutral. |
| `/framework` | Three short docs that codify the discipline: the FACT/HYPOTHESIS/SPECULATION grade ladder, the audit habit, and the find→review loop. |
| `/architecture` | One markdown file describing the four-agent pipeline at the level of inputs, outputs, and hand-off contracts. No code. |
| `/backtest_skeleton` | The structural shell of the backtest engine — entry/exit/metrics interfaces with placeholder rule definitions. Drop your domain rules in. |
| `/examples/neutral_corpus` | A worked example applied to a safe public corpus, end-to-end. |
| `SANITIZATION_REPORT.md` | What was kept, what was sanitized, where the placeholders sit. Read this before deploying to your domain. |

## Reading order for a new user

1. `README.md` (this file) — orientation.
2. `framework/fact_hypothesis_speculation.md` — the grading discipline. Without this, the rest produces noise.
3. `framework/audit_discipline.md` — why plausible isn't true.
4. `architecture/four_agent_pipeline.md` — how the work flows.
5. `examples/neutral_corpus/00_overview.md` — see the discipline applied.
6. `prompts/00_README.md` — when you're ready to run it on your own corpus.
7. `backtest_skeleton/README.md` — when you have rules ready to test.

## What this method is not

- **Not a content extractor.** Off-the-shelf RAG and summarization are good at "what did the source say?" — that's not the bottleneck. The bottleneck is grading what they said and testing what survives.
- **Not a sentiment or stylometry tool.** The output is a tested rule set, not a vibe.
- **Not a substitute for domain expertise.** You still need someone who can recognize when a rule is sound vs. when the source was joking. The framework just stops you from baking jokes into the rule set.
- **Not a finished product.** Each domain demands its own backtest definition. The skeleton is structural; the rules are yours.

## Naming convention used in placeholders

| Placeholder | Means |
|---|---|
| `{ENTITY}` | The expert whose method you're decoding. |
| `{INVESTIGATOR}` | You, the researcher running the pipeline. |
| `{DOMAIN}` | The field of practice (e.g. code review, editorial, clinical, etc.). |
| `{RULE_NAME}` | The expert's name for their own framework, if they have one. |
| `{CORPUS_A}`, `{CORPUS_B}`, … | Each text channel (chat platform, mailing list, email, etc.). |
| `{CORPUS_FILE_A}`, `{CORPUS_FILE_B}`, … | The actual file/export of each corpus. |
| `{ARTIFACT}` | The unit of evaluation — what one decision applies to (e.g. one PR, one paper draft, one chart). |
| `{OUTCOME}` | The measurable ground truth (accept/reject, hit/miss, etc.). |
| `{GRANULARITY}` | The time or context resolution (a day, a session, a paragraph). |
| `{WINDOW}` | A subset of granularity in which the expert claims edge (a session, a phase). |
| `{METRIC_X}` | A claimed performance number (deliberately not stated; you measure your own). |

You substitute these when you instantiate the prompts and the engine for your own domain.

## License and provenance

This methodology was extracted from a private, year-long reverse-engineering project applied to a single domain. Every reference to that domain has been replaced with placeholders. See `SANITIZATION_REPORT.md` for the full audit of what was scrubbed.

The method itself is not the property of any one project — it's the disciplined application of techniques that are common across investigative research, qualitative coding, and quantitative validation. What is novel here is the integration: the four-agent pipeline, the FACT/HYPOTHESIS/SPECULATION grade ladder applied to a tacit-knowledge corpus, and the find→review loop that closes the gap between "we extracted a rule" and "the rule produces the claimed outcome."
