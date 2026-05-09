# Walkthrough — phase by phase, with neutral-domain content

This is the abridged narrative of running the full methodology against an open-source code-review corpus. Each phase shows what comes in, what goes out, and what an audit catches.

## Phase 1 — Intake (Prompts 1 + 2)

### Run Prompt 1: chronological read of `prs.jsonl`

The orchestrator spawns sub-agents, one per quarter of activity. Each sub-agent reads PR reviews and returns verbatim quotes that hint at the maintainer's rules.

Sample sub-agent return (anonymized — every name and project ref is a placeholder):

```
[2022-04-12 09:14:21] {ENTITY}: "I don't merge breaking changes without a deprecation cycle. Add a warning in 0.21, remove in 0.22."
   context: PR #1284, refactor that broke a public function signature

[2022-08-30 17:02:08] {ENTITY}: "We don't add dependencies for one-line helpers. Inline it."
   context: PR #1567, adding a small utility from a 3rd-party lib

[2023-01-04 22:17:55] {ENTITY}: "lol yeah merge it" 🍻
   context: PR #1932, junior contributor first-time PR with a typo fix
```

The third quote is structurally interesting — it looks like a rule violation. The maintainer "merged without review" of a PR that touches code. But the audit will catch the goofing-tone (lol + 🍻 + junior contributor + typo-fix-only) and downgrade it.

After all sub-agents return, the orchestrator de-duplicates against the existing Facts Log and produces a per-theme grouping:

- **Theme: scope discipline** (15 quotes)
- **Theme: deprecation policy** (8 quotes)
- **Theme: testing requirements** (22 quotes)
- **Theme: dependency management** (11 quotes)
- **Theme: meta / off-topic** (4 quotes; flagged for audit)

### Run Prompt 2: read of `mailing_list.mbox`

Same shape, but on the lower-volume mailing list. Returns ~30 new quotes plus 3 corrections to Prompt 1 quotes (where the mailing-list version was the original and the GitHub comment was a quote of it).

The mailing list often contains the *reasoning* behind the GitHub rules. So while Prompt 1 captures *"don't merge breaking changes without a deprecation cycle"*, Prompt 2 might capture *"the reason we have a deprecation cycle is that downstream packagers fork our releases and a hard break causes 6 months of triage emails."* The reasoning is what makes the rule a teachable principle rather than an arbitrary policy.

## Phase 2 — Synthesis (the orchestrator's role inside Prompts 1 + 2)

The orchestrator turns the verbatim quotes into Findings. Sample new Finding draft:

```
### Finding 7 — Deprecation cycle is required for breaking changes
Status: HYPOTHESIS

Source quotes:
> "I don't merge breaking changes without a deprecation cycle. Add a warning in 0.21,
>  remove in 0.22." (PR #1284, 2022-04-12)
> "downstream packagers fork our releases and a hard break causes 6 months of triage
>  emails." (mailing list, 2022-04-15)
> "[third quote, similar effect]" (PR #2104, 2022-09-30)

Falsification rule:
  Find ≥3 merged PRs that introduced a breaking change without a deprecation
  warning. If found, the rule does not hold universally.
```

Three independent quotes across two channels and three months. Direct teaching tone. Internally consistent (the GitHub rule has a stated rationale in the mailing list). HYPOTHESIS-grade pending the falsification test.

## Phase 3 — Audit (the separate audit pass)

The auditor reads every new Finding and grades:

- 🟢 SOLID — repeated across multiple channels, verbatim, in serious-teaching tone.
- 🟡 WORTH-CHECKING — single mention or ambiguous, but plausible.
- 🟠 GOOFING-RISK — joke tone, reactive emoji, isolated context.
- 🔴 DEPRECATED — explicitly retracted or contradicted by data.

Sample audit findings:

```
Finding 7 (deprecation cycle):  🟢 SOLID — 3 quotes across 2 channels, with a stated
  rationale and no contradicting quotes. Recommendation: USE.

Finding 11 (typo-fix shortcut): 🟠 GOOFING-RISK — single mention, "lol yeah merge it",
  emoji 🍻, junior contributor first PR, scope is a typo only. The maintainer was
  being relaxed about a low-stakes case, not announcing a policy. Recommendation:
  DO NOT use as a general "low-stakes PRs need no review" rule.

Finding 14 (no new dependencies): 🟢 SOLID — 11 supporting quotes across 3 years.
  Recommendation: USE.
```

Now we have an audited Findings list. Notice that the goofing-risk catch is the audit's main job — if you used Finding 11 as a rule, your engine would systematically over-predict acceptance for typo-fix PRs and miss the cases where the maintainer rejected typo-fix PRs that touched the wrong file.

## Phase 4 — Backtest (Prompts 5 + 6)

You build the engine. The shape from `backtest_skeleton/` adapts: instead of `Primitive` having a numeric value, it's a Boolean criterion. Instead of `find_active_pair`, you check which criteria fire for a given PR. Instead of `simulate_event`, you predict accept/reject based on which criteria fire.

### Phase 1 validation (Prompt 5)

Run the predicted accept/reject against a *training* set of 400 PRs. Compute hit rate.

Sample baseline result:

- N = 400 PRs
- Prediction accuracy: 71%
- False accepts (predicted accept, actually closed): 14% — usually scope mismatches
- False rejects (predicted reject, actually merged): 15% — usually exception cases the rules don't cover

71% is plausible. The maintainer's articulated rules in `CONTRIBUTING.md` alone would probably give 55–60%. So our extracted Findings are adding real signal.

### Phase 2 orchestration (Prompt 6)

Sweep filter conditions. Each iteration adds one filter, measures the lift, keeps or drops.

Sample iteration log:

```
Iter 0: baseline                    | n=400 | 71%   | exp +0.42
Iter 1: + scope-mismatch detector   | n=400 | 78%   | exp +0.56 | KEEP
Iter 2: + author-track-record       | n=400 | 81%   | exp +0.63 | KEEP
Iter 3: + sibling-PR cross-link     | n=400 | 81%   | exp +0.63 | DROP (no lift)
Iter 4: + release-cycle phase       | n=400 | 83%   | exp +0.70 | KEEP
```

Three filters lift the hit rate from 71% to 83%. The orchestrator stops when no further single filter adds ≥1 pt.

## Phase 5 — External calibration (Prompt 8)

Now we evaluate on the **held-out set** of 100 PRs we set aside in setup step 6.

```
Final config:
  - Filters: scope-mismatch + author-track-record + release-cycle phase
  - Engine prediction on held-out N=100 PRs

Held-out hit rate: 81%

Comparison:
  - CONTRIBUTING.md alone (the articulated rule set): ~58% on the same held-out
  - Our reverse-engineered rule set: 81%
  - Δ: +23 pts

Residual: 19% of the maintainer's decisions are not predicted by our rule set.
```

What does the residual contain? Look at the misses.

- 8 of 19 misses are **edge cases the rule set didn't cover** (e.g. a PR that's both breaking and trivial — neither rule applies cleanly). These could potentially be addressed with more rules.
- 6 of 19 are **maintainer mood / context** — the same kind of PR was accepted in week 12 and rejected in week 24. The rule set can't model this.
- 5 of 19 are **rare patterns** that didn't appear enough in the training corpus to become Findings.

The 6 mood/context misses are the **non-recoverable** layer. They're the equivalent of the deleted-DM layer in the original investigation. You measure them; you don't try to eliminate them.

## What you can say at the end

- "The maintainer's tacit rule set is reproducible from the public corpus to 81% accuracy."
- "Of the residual 19%, 11% is in principle recoverable with more corpus mining; 6% appears to be non-mechanical context the maintainer doesn't articulate consistently."
- "The articulated CONTRIBUTING.md alone reproduces only ~58%. The extracted Findings add 23 pts of explanatory power."
- "The Findings_Audit.md catches X goofing-risk patterns that, if treated as rules, would have misled the engine."

That's a publishable result, with full provenance. Anyone with access to the corpus could reproduce it in days; the discipline is what makes it credible.

## Lessons that transfer to your domain

- **The audit catches more value than the synthesis.** Without the audit, the Finding 11 typo-fix rule would have been baked in. With the audit, it gets caught.
- **The held-out set is non-negotiable.** Without it, you can't tell if your final 83% is real or overfit. With it, you can.
- **The residual is informative.** Don't try to eliminate it. Decompose it: how much is recoverable, how much is not?
- **Articulated baselines matter.** The CONTRIBUTING.md baseline (55–60%) tells you what the *documented* rule set produces. Anything you add beyond that is the *tacit* layer. Without the baseline you have no calibration for what "extracted via Solomon method" actually contributed.
