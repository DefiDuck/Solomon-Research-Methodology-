# The audit discipline

The complement to the FACT/HYPOTHESIS/SPECULATION grading. Grading is local — applied to each new claim as it enters. Auditing is global — applied periodically to the entire body of claims.

The audit answers three questions about every Finding:

## The 3 audit questions

For every Finding in your `KEY_FINDINGS.md`:

### 1. Was the source teaching, or goofing?

Sources who write a lot say a lot of things they don't mean. They make jokes, troll, vent, and sometimes deliberately misdirect (especially in public channels with multiple observers).

Mark each Finding with one of:

- 🟢 **SOLID** — verbatim, repeated multiple times across months, in serious-teaching tone, in a high-trust channel. Low goofing-risk.
- 🟡 **WORTH CHECKING** — supported but with weak spots: single mention, ambiguous tone, public-channel context, or contradicted by another quote. Worth a gut check.
- 🟠 **GOOFING-RISK** — single mention, joke tone, public-channel context, around emoji clusters or other troll markers. Don't bake into rules until further evidence.
- 🔴 **DEPRECATED** — already retracted by the source or falsified by data. Listed for completeness so it doesn't accidentally resurrect.

The discipline: **never treat a 🟠 GOOFING-RISK Finding as load-bearing.** If a downstream Finding depends on a 🟠 Finding, both inherit the goofing-risk.

### 2. Is the verbatim quote actually saying what we think it's saying?

The source's words mean what *they* meant by them, not what *you* meant when you read them. The audit forces you to re-read the quote with deliberate skepticism:

- Could this quote be sarcastic? (Look at surrounding messages.)
- Could "always" / "never" / "every" be hyperbole? (The source themselves often admits hyperbole later.)
- Is the quote in response to a specific scenario, and we generalized it incorrectly?
- Did the source contradict this quote later? (Check the timeline.)

If any of these checks fires, downgrade the Finding's grade or status.

### 3. Have we tested the testable parts?

For every HYPOTHESIS in the Findings, ask:
- Has the falsification test been run? (If no, run it or mark as untested.)
- Was the test sample big enough? (Typical bar: N≥50 events for promotion to FACT; N≥10 for direction.)
- Was the test out-of-sample, or did we tune the rule on the test data? (If tuned, the test is invalid.)

For every FACT, ask:
- Has it been re-tested recently? (Some FACTs decay if the source's setup changed.)
- Is it really FACT-grade, or did we promote prematurely?

## When to audit

- **Every 4–6 weeks** during an active investigation. The corpus has grown; the audit re-calibrates.
- **Before any major deliverable** (report, book chapter, public release). The audit catches the embarrassing claims before publication.
- **After any new high-trust source** is added (e.g. you got access to a new channel). The new evidence may upgrade or downgrade existing Findings.
- **Before promoting anything to FACT.** Always audit-then-promote, never promote-then-audit.

## The audit artifact

The audit produces a single document: `Findings_Audit.md`. Format:

```
# Findings Audit — YYYY-MM-DD

For each Finding:

### Finding NN — [headline claim]
**Status (current):** FACT / HYPOTHESIS / SPECULATION / DEPRECATED
**Trust ring (audit verdict):** 🟢 SOLID / 🟡 WORTH CHECKING / 🟠 GOOFING-RISK / 🔴 DEPRECATED
**Source(s):**
> "verbatim quote 1" (timestamp, channel)
> "verbatim quote 2" (timestamp, channel)
**Smell test:** 1-2 sentences on whether the source was teaching or goofing.
**Recommendation:** USE / TEST / RETIRE.
**Auditor note:** _____________
```

The auditor note column is for the human running the audit. It's where you record your gut check, contradicting evidence you noticed, follow-up questions to investigate.

## Plausible is not true

The single biggest trap in this kind of investigation: claims that *sound right* slip into the Findings without verbatim support. They feel coherent because they fit the narrative. They might even be correct. But "might be correct" is not the same as "is correct."

The audit's job is to repeatedly ask: **does this Finding survive a strict re-grading, or does it only feel right?** Plausibility is the seductive failure mode. The audit is the antidote.

## Who runs the audit

In a multi-agent pipeline (see `architecture/four_agent_pipeline.md`), the Audit role is a **distinct agent** from the Synthesis role. The Synthesis agent has a stake in their Findings being accepted. The Audit agent does not. Separating them protects against confirmation bias.

If you don't have multiple agents, separate the roles in time: write Findings now, audit them in 1–2 weeks. The temporal separation provides part of the same effect.

## Don't audit yourself in real time

Auditing in real time, at the moment a claim is being formed, is exhausting and produces under-claiming (you become too conservative). The audit habit works best as a periodic batch — write claims confidently when you're synthesizing, then audit them coldly when you're auditing.
