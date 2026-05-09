# Prompt 8 — External calibration vs {ENTITY}'s verbatim claim

**Copy everything below this line into Claude Code.**

---

This is the final scoreboard. You combine three numbers and produce one calibration result with full provenance:

1. The historical backtest result (Prompts 5 + 6).
2. The live-event accumulation (Prompt 7).
3. {ENTITY}'s verbatim performance claim (from your Facts Log, with the exact timestamp and channel).

The deliverable is a single document any third party can audit. It says: here is what {ENTITY} claimed; here is what we measured; here is the residual gap; here is the provenance for every number.

This is what you would publish, hand off to a stakeholder, or attach as evidence in any external review.

**You are in the project root.** Read these files first:
1. `findings/KEY_FINDINGS.md` — locate every verbatim {ENTITY} performance claim. Quote each exactly with its timestamp and channel.
2. `engine/runs/PHASE_2_SUMMARY.md` — your best historical metric.
3. `engine/runs/live_events_log.md` — your live metric, if available.
4. `findings/Findings_Audit.md` — the trust-grade for each claim you're calibrating against.

## The three numbers

For each claim {ENTITY} has made about their performance, compute three numbers:

| Number | Source | What it answers |
|---|---|---|
| **claimed** | Verbatim {ENTITY} quote, highest-trust channel ({CHANNEL_SECONDARY}) | What does the source say their performance is? |
| **historical_measured** | Best Phase 2 config metric on historical data | What does the documented rule set produce on historical data? |
| **live_measured** | Same config applied to live-event window | Does the rule set still produce that performance going forward? |

Then compute:

- **Historical residual:** claimed − historical_measured
- **Live residual:** claimed − live_measured
- **Stability:** historical_measured − live_measured

## Interpretation rubric

| Historical residual | Verdict |
|---|---|
| ≤ 5 pts | **VALIDATED.** The reverse-engineered rule set reproduces the claim within margin. The framework is empirically sound. |
| 5–10 pts | **STRONG.** Residual likely lives in non-recoverable channels (deleted DMs, real-time pattern recognition, undocumented filters). Document the residual; don't keep tuning. |
| 10–20 pts | **PARTIAL.** Either the source's claim is exaggerated, or there's a major rule we haven't identified. Re-investigate the corpus for missed Findings before publishing. |
| > 20 pts | **NOT VALIDATED.** The claim and the measured result are too far apart to publish honestly. Either the framework is incomplete, or the source's claim is pure marketing. Investigate which. |

| Stability (historical vs live) | Verdict |
|---|---|
| ≤ 3 pts | **DURABLE.** Rules generalize forward in time. Investigation is publishable. |
| 3–5 pts | **STABLE-ISH.** Some drift but within noise. Re-check in another month. |
| > 5 pts | **DRIFTING.** Either the source's setup has shifted, or the historical sample was over-fit. Don't publish as a stable result; flag the drift in the deliverable. |

## Deliverable

`reports/EXTERNAL_CALIBRATION.md`. Format:

```
# External Calibration: {RULE_NAME}
Date: YYYY-MM-DD
Investigator: {INVESTIGATOR}

## Headline numbers
- Claimed:              X.X% (verbatim {ENTITY} quote, see provenance)
- Historical measured:  Y.Y% (n=N events, window {start}-{end})
- Live measured:        Z.Z% (n=M events, captured {start}-{end})
- Historical residual:  ±A pts
- Live residual:        ±B pts
- Stability:            ±C pts

## Verdict
[Pick from rubric above.]

## Provenance — claimed
- Quote: "[exact verbatim string]"
- Timestamp: YYYY-MM-DD HH:MM:SS
- Channel: {CHANNEL_SECONDARY} (highest-trust)
- Trust grade (per Findings_Audit): 🟢 SOLID / 🟡 WORTH-CHECKING / 🟠 GOOFING-RISK
- Caveats: [any reason to discount, e.g. surrounding hyperbole, joke tone]

## Provenance — historical_measured
- Run config: [yaml block from PHASE_2_SUMMARY.md]
- Window: [start, end]
- Sample size: N events
- Data source: [adapter name + version]
- Reproducibility: every input file is in /engine/runs/_data_cache/

## Provenance — live_measured
- Receiver started: YYYY-MM-DD
- Capture window: [start, end]
- Sample size: N events
- Capture method: webhook / polling / hybrid
- Re-run config: identical to historical (no re-tuning)

## Caveats and known limitations
- [out-of-sample discipline: did Phase 2 tune on the same window as historical_measured? If yes, hold out 25% next time.]
- [non-recoverable channels: any private channel content we know exists but cannot access]
- [data adapter limits: any window where the adapter dropped data]
- [survivorship bias: any selection effect in which events made it into the corpus]

## Recommendations
- Should we publish the framework?  [yes / no — with reason]
- What changes the answer?           [e.g. "yes if live sample reaches N=200"]
- Next investigation step             [if any]
- Live-event projection               [project the residual at N=200, N=500, N=1000 and see when the confidence band tightens enough to flip the verdict]
```

---

## Important discipline

- **Treat `claimed` as a verbatim quote, not as truth.** Document the trust grade. If the claim is from a public channel where you have evidence of misdirection, downgrade it on the trust ladder.
- **No retroactive cherry-picking.** If your Phase 2 was tuned on the same window you're using to compute `historical_measured`, you're double-counting. Hold out at least 25% of the window as out-of-sample if you possibly can. Note when you cannot.
- **Document the gap honestly.** "Within 5 pts" is the standard for VALIDATED. Be explicit when your residual is wider, and resist the temptation to keep tuning until the verdict moves up a tier — that's overfitting in slow motion.
- **Don't pad provenance.** Every number in the headline must trace to a single config in `engine/runs/`. If you can't draw the line, don't publish.

## What this prompt produces

A single document an external auditor could read in 10 minutes and either (a) reproduce your numbers from your data caches, or (b) identify exactly where the methodology fell short. That auditability is the entire point.

When complete, present the calibration result to the user. This is the final score for the entire reverse-engineering project.
