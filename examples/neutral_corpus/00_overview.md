# Overview — the worked example

## Setting

You pick an open-source project. It must have:

- A single primary maintainer (or a small group with consistent style).
- ≥3 years of public PR activity.
- ≥500 closed PRs (mix of merged and closed-without-merge).
- Public review comments on most PRs.

A few candidate categories (you pick one specific project):

- **Reference implementation projects** — maintainers tend to have strong opinions about API stability and backward-compat.
- **Toolchain projects** (compilers, build systems) — maintainers tend to care about correctness and benchmarks.
- **Library projects with strict scope** — maintainers reject features that are out of scope, regardless of code quality.

Don't pick a project where the maintainer is also publicly visible on social media commenting on their decisions, because that creates a contamination channel — you'd want to keep that as a separate corpus.

## Placeholder substitutions

Throughout this walkthrough, the placeholders from the public methodology resolve as:

| Placeholder | Resolves to |
|---|---|
| `{ENTITY}` | the project's primary maintainer |
| `{INVESTIGATOR}` | you, the researcher |
| `{DOMAIN}` | open-source maintainership |
| `{RULE_NAME}` | "Maintainer-X's merge criteria" (or whatever the maintainer themselves calls it, if anything) |
| `{CORPUS_A}` | the project's PR comment archive (the highest-volume corpus) |
| `{CORPUS_B}` | the project's mailing list / Discord / forum archive (lower-volume but often higher-trust) |
| `{CORPUS_FILE_A}` | exported PR comments (e.g. via GitHub GraphQL into `prs.jsonl`) |
| `{CORPUS_FILE_B}` | exported mailing list mbox or forum dump |
| `{ARTIFACT}` | one PR (the unit of evaluation) |
| `{OUTCOME}` | merged / closed-without-merge (the binary ground truth) |
| `{GRANULARITY}` | not strictly applicable — there's no time-resolution; replace with "per-PR" |
| `{WINDOW}` | optional; could be "release candidate weeks" vs "stable weeks" if the project has a release cycle that affects merge behavior |
| `{SIGNAL_FEATURE}` | a single decision criterion (e.g. "PR has tests", "PR touches public API", "PR has issue link") |
| `{ACTIVE_PAIR}` | not applicable in this domain — adapt the rule set; see below |
| `{MIDPOINT}` | not applicable; the entry trigger is a Boolean predicate, not a value |
| `{ENTRY_RULE}` | "predict the maintainer would accept this PR if all of {C1, C2, …, Ck} hold" |
| `{EXIT_RULE}` | "predict the maintainer would reject if any of {R1, R2, …, Rk} hold" |
| `{TIME_STOP_N}` | replaced by "stop predicting after the maintainer's first review comment" — the analog of a deadline |

The placeholder mapping is the work. Once you've done it for your domain, the prompts become directly applicable.

## Adaptation note

The original methodology was extracted from a domain where the rule set acts on numeric values and identifies an "active pair" of nearby reference points. In this code-review domain, the active-pair concept doesn't apply directly. You replace it with a Boolean rule pipeline:

- **Validated primitives** → Boolean criteria the maintainer applies (each must have ≥3 same-type appearances in the review corpus to be valid).
- **State classification** → context categories (e.g. "minor patch", "feature", "breaking change"). Different criteria apply per state.
- **Active pair / midpoint** → drop. Replace with a scoring function that combines the validated criteria.
- **Entry rule** → predict-accept threshold.
- **Exit rule** → predict-reject threshold.
- **Time stop** → "after maintainer's first review comment, stop predicting."

This domain adaptation is where the user's judgment shows up. The engine skeleton supports the shape; you decide how to map your domain into it.

## What you produce

Three artifacts, in order:

1. **The Facts Log** — a JSONL of every direct maintainer quote, each tagged with PR number, timestamp, and category.
2. **The Findings file** — a Markdown of graded criteria (FACT / HYPOTHESIS / SPECULATION).
3. **The backtest report** — a CSV of held-out PRs with predicted vs actual outcome, plus an aggregate hit-rate number.

The third artifact is the calibration — what % of the time does the documented rule set correctly predict accept/reject? That number, with full provenance, is the deliverable.
