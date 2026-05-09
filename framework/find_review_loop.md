# The Find → Review loop

The structural shape of the investigation. You alternate between two modes:

- **Find:** read the corpus, extract evidence, form claims.
- **Review:** audit the claims you just made, run their falsification tests, demote / promote / deprecate.

You never just Find. You never just Review. The whole methodology is the alternation.

## The loop in one diagram

```
        ┌─────────────────────────────┐
        │                             │
        │   FIND                      │
        │   ───────────               │
        │   • read corpus chunk       │
        │   • extract verbatim quotes │
        │   • propose new Findings    │
        │   • grade FACT/HYP/SPEC     │
        │                             │
        └──────────────┬──────────────┘
                       │
                       │ (every 4-6 weeks
                       │  or after any
                       │  major deliverable)
                       │
        ┌──────────────▼──────────────┐
        │                             │
        │   REVIEW                    │
        │   ───────────               │
        │   • audit each Finding      │
        │   • run falsification tests │
        │   • demote / promote        │
        │   • mark goofing-risk       │
        │                             │
        └──────────────┬──────────────┘
                       │
                       │
                       ▼
                 (back to FIND with
                  refined questions)
```

## What "Find" produces

Each Find pass produces three artifacts:

1. **New verbatim quotes** appended to the Facts Log (with timestamps and channel).
2. **New Findings** appended to the Findings file (each graded).
3. **New Open Questions** appended to the Open Questions queue (with falsification rules).

Find is **additive only**. Find never deletes or downgrades existing Findings. That's Review's job.

## What "Review" produces

Each Review pass produces two artifacts:

1. **Findings_Audit.md** — the trust audit at this moment in time. Replaces the prior version.
2. **A diff list** — every Finding whose grade or status changed in this audit, with the reason.

Review is **subtractive and re-grading**. Review never adds new Findings; it can only refine existing ones.

## Why the alternation matters

If you only Find, you accumulate confident-sounding claims that are partially or fully wrong. The investigation becomes a pile of plausible-but-untested hypotheses.

If you only Review, you starve. You can't refine claims that aren't being added.

The alternation forces both: enough corpus reading to keep adding evidence, plus enough auditing to keep the existing pile honest.

## Cadence

A typical investigation runs at this cadence:

- **Find phase:** 1–2 weeks of corpus reading + Findings drafting.
- **Review phase:** ~3 days. Audit, run any pending falsification tests, write the Findings_Audit.md.
- **Repeat.**

Some investigations are shorter (a single corpus chunk, single Find + single Review). Some are years long. The cadence scales but the alternation is invariant.

## When to interrupt the loop with a backtest

The backtest engine (Prompts 5–6 in the prompt sequence) is a special kind of Review. It's heavy enough that you don't run it every Review pass — usually after the corpus is ~80% mined and the rule set has stabilized.

The backtest's job is to **convert HYPOTHESES into FACTs at scale.** A normal Review can run a single falsification test. The backtest engine runs hundreds in parallel. Use it when:

1. You have a stable rule set (Find phase has plateaued — fewer new quotes per pass).
2. You have ground-truth data to test against.
3. You want to know which subset of HYPOTHESES are actually load-bearing.

Run the backtest. Update the Findings with the results. Resume Find/Review on the questions the backtest exposed.

## When to stop the loop

The loop can stop in three ways:

1. **All FACTs reproduced externally:** the backtest engine measures within tolerance of the source's claimed metric. The reverse-engineered rule set is empirically validated. Stop and ship.
2. **Sample exhaustion:** the corpus has been fully read, no new Findings are being added per Find pass, and the residual gap is stable. Stop and document the residual.
3. **Decision to deploy:** the rule set is good enough for the use case (forward-testing on real activity). Stop the offline loop and start collecting live data (Prompt 7).

## Failure modes

- **Find without Review.** Pile of unaudited claims. Confident garbage.
- **Review without Find.** Audit finds nothing new because no new claims came in. Wasted cycle.
- **Skipping the audit's hard questions.** "I'll mark it 🟢 SOLID for now and audit properly later." Later never comes. The 🟢 ossifies into "fact" without ever being properly tested.
- **Editing claims during Find.** Tempting to "fix up" an existing claim while you're in Find mode. Don't. Add a new claim instead and let Review reconcile them. Otherwise you lose the version history.

## The single discipline that makes this work

Treat your own previous claims with the same skepticism you'd apply to a stranger's. The source you're reverse-engineering doesn't get to defend their claims. Your past self doesn't either. Both are read coldly; both are audited the same way.
