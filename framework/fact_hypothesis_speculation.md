# The FACT / HYPOTHESIS / SPECULATION grade ladder

Every claim in a Solomon investigation gets exactly one of three grades. Without this discipline, the corpus turns into a confidence game where plausible statements become load-bearing without anyone noticing.

## The three grades

### 🟢 FACT
A claim backed by either:
- A direct verbatim quote from the corpus (timestamp + exact text), OR
- An externally-verifiable measurement (a third-party data source, a reproducible computation).

A FACT can be wrong about its meaning, but the artifact behind it is real. *"On 2024-03-12 at 14:22, the source said X"* is a FACT because the timestamp and string are checkable. Whether X means what you think it means is a separate question, graded separately.

### 🟡 HYPOTHESIS
A testable proposition with a defined falsification rule. The proposition can be plausible, internally consistent, even widely believed — none of that grants it FACT status. A HYPOTHESIS is open until either:
- N ≥ 3 independent confirmations make it provisionally a FACT, OR
- One clean falsification retires it.

The defined falsification rule is the half people skip. *"This is probably true"* is not a HYPOTHESIS — it's a SPECULATION wearing better clothes. *"This is true if and only if a 50-trade backtest shows ≥60% win rate; otherwise false"* is a HYPOTHESIS.

### 🟠 SPECULATION
A working idea without a defined test yet. Useful for scoping. Dangerous if restated as fact. SPECULATIONS get flagged inline so you can revisit them when more evidence arrives.

The investigator's job is to either upgrade SPECULATIONs to HYPOTHESES (by defining the test) or retire them.

## The forbidden grade: "supported by"

Beware the language *"this is supported by"*, *"consistent with"*, *"plausibly explained by"*. These phrases let a claim drift up the ladder without earning the position. They're how SPECULATIONS become FACTS in casual writing.

When you find one of those phrases in your own draft, replace it with a grade. The replacement might be: *"This is HYPOTHESIS-grade pending the test in section 4."* That's honest. The original was just rhetoric.

## Examples (from a neutral domain — open-source code review)

To make the discipline concrete, here are graded claims about a hypothetical maintainer's PR-review behavior. Replace the maintainer with your domain expert.

| Claim | Grade | Why |
|---|---|---|
| *"On 2023-07-04, the maintainer wrote in PR #2451: 'I don't accept PRs without tests'."* | **FACT** | Direct verbatim quote with timestamp and PR number. Verifiable by opening the PR. |
| *"The maintainer rejects all PRs without tests."* | **HYPOTHESIS** | Plausible inference from the FACT above, but it's a universal claim. Falsification: find one PR the maintainer accepted without tests. The test is defined; the claim is testable. |
| *"The maintainer's review style reflects an emphasis on rigor over speed."* | **SPECULATION** | True or false, you can't currently test it without operationalizing "rigor" and "speed" first. Flag for later. |
| *"In this commit message, the maintainer wrote 'lol just merge it'."* | **FACT** | Verbatim. |
| *"The 'lol just merge it' comment shows the maintainer doesn't actually require tests."* | **SPECULATION** (and probably wrong) | A joke quote can't override a stated rule. This is the **goofing risk** — see `audit_discipline.md`. |

## Why this matters

Investigations on a tacit-knowledge corpus tend to fail in two ways:

1. **The investigator over-believes the source.** They take every utterance as method, including the jokes, the frustration vents, and the deliberate misdirection. The "rule set" they extract is half-truth, half-noise.

2. **The investigator under-believes the source.** They demand mathematical proof for what is, in fact, a verbatim teaching. The rule set is too cautious to be useful.

The grade ladder calibrates between these failure modes. FACT requires evidence, HYPOTHESIS requires a test, SPECULATION is honest about its provisional status. You can't accidentally promote.

## When you finish a draft

Before declaring an analysis complete, audit every claim for grade. If a claim has no grade, give it one. If you can't justify the grade, demote until you can.

The result is a document where every sentence has measurable epistemic weight. That's what makes it composable with the audit and backtest layers downstream.

## Common errors to watch for

- **Frequency illusion.** "The source repeats this often" is a SPECULATION about frequency until you count. Count.
- **Confirmation by adjacency.** "The source said X near Y, so X explains Y." That's a SPECULATION. The proximity could be coincidence. Test it as a separate claim.
- **Authority laundering.** "The source said this on day 1, then again on day 200, so it's solid." Repetition isn't independent evidence — it's the same source repeating themselves. Independent evidence comes from a different channel (e.g. third-party verification, ground-truth measurement).
- **The completed-puzzle bias.** Once you've drafted a coherent rule set, every new quote will appear to "support" it. Run the audit *against* your rule set, not for it. Look for contradicting quotes specifically.

## Operational checklist

When grading a claim, ask in order:

1. Is there a verbatim quote with a verifiable source? → If yes, **FACT**.
2. Is there a defined falsification test? → If yes, **HYPOTHESIS**.
3. Otherwise → **SPECULATION**, and either define the test or accept the provisional status.

Three questions, one minute. Do this for every claim that ends up in the canonical document. The discipline is the deliverable.
