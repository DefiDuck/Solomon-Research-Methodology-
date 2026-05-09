# Worked example — decoding an open-source maintainer's tacit code-review criteria

A minimal end-to-end walkthrough that applies the Solomon method to a safe public corpus: an open-source project's pull-request review history.

The pattern: a project has a single primary maintainer who has reviewed thousands of PRs over years. Their merge criteria are partly documented (the `CONTRIBUTING.md`) and partly tacit (years of review comments, accepted/rejected decisions, follow-up issue threads). You can:

1. Read the corpus (PR reviews, commit messages, related issue threads, mailing list archives).
2. Extract verbatim quotes that hint at criteria.
3. Audit them — which are real teaching, which are jokes or tired venting.
4. Backtest the extracted rules against held-out PRs (predict accept/reject).

This example shows the shape of each phase. **No specific maintainer or project is named.** You can swap in any project whose review history is public and large enough.

## Files in this example

- `00_overview.md` — the framing of the worked example.
- `01_setup.md` — how to instantiate the methodology for this domain.
- `02_walkthrough.md` — phase-by-phase walkthrough with the placeholders filled in.

## Why this corpus is a good example

- **Public.** PR reviews on a popular open-source project are publicly readable. No privacy or NDA concerns.
- **Large.** A project with 5+ years of activity has hundreds to thousands of reviewed PRs. Plenty of corpus.
- **Tacit-heavy.** The maintainer's actual decision criteria are partly undocumented. CONTRIBUTING.md captures ~30% of what gets a PR accepted; the rest lives in review comments.
- **Testable.** Every PR has a binary outcome (merged, closed-without-merge). The backtest predicts the outcome. Hit rate is mechanical.
- **Multi-channel.** PR comments, commit messages, related issues, mailing list — multiple corpora, ranked by trust.

If your project doesn't have all of these properties (e.g. the corpus is small, or the outcome isn't binary), the example still applies — you just have to scale the size of the prompts and the backtest accordingly.

## What you'll have at the end of the walkthrough

- A `Findings_Audit.md`-style document listing the maintainer's tacit criteria, each graded FACT/HYPOTHESIS/SPECULATION.
- A working backtest engine that predicts PR accept/reject.
- A residual gap number: how often the engine's prediction matches the maintainer's actual decision.

If the residual gap is small, you can hand the rule set to a new contributor as "things this maintainer cares about." If the residual is large, you have measured the *gap between articulated rules and tacit practice* — itself a useful research output.
