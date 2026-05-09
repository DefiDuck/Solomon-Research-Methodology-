# The 4-agent pipeline

A high-level architecture for running the Solomon method at scale. Four roles, four hand-off contracts. Each role can be played by a separate Claude Code session, a separate human, or the same agent in different sessions — what matters is that the **roles are distinct** and the **contracts between them are explicit**.

## The roles

```
   ┌───────────────┐    quotes    ┌───────────────┐    findings   ┌───────────────┐    rules     ┌───────────────┐
   │               │ ───────────► │               │ ────────────► │               │ ───────────► │               │
   │   1. INTAKE   │              │  2. SYNTHESIS │               │   3. AUDIT    │              │  4. BACKTEST  │
   │               │              │               │               │               │              │               │
   │  reads corpus │              │ groups quotes │               │  re-grades    │              │ runs engine,  │
   │  pulls quotes │              │ proposes new  │               │  every claim  │              │ measures hit  │
   │  by date or   │              │ Findings,     │               │  per audit    │              │ rate vs       │
   │  feature key  │              │ grades each   │               │  discipline   │              │ baseline      │
   │               │              │ FACT/HYP/SPEC │               │               │              │               │
   └───────────────┘              └───────────────┘               └───────────────┘              └───────────────┘
```

## Role 1 — INTAKE

### Inputs
- Raw corpus files (`{CORPUS_FILE_A}`, `{CORPUS_FILE_B}`, image folders)
- Existing Facts Log (so it doesn't re-extract known quotes)
- Existing Findings file (so it knows what categories of evidence we're after)

### Outputs
A **set of new verbatim quotes** with full provenance:

```yaml
- quote: "exact verbatim text"
  speaker: "{ENTITY}"
  timestamp: "YYYY-MM-DD HH:MM:SS"
  channel: "{CHANNEL_PRIMARY} or {CHANNEL_SECONDARY}"
  context: "1-line description of surrounding messages"
  category: "primitive | exit | window | risk | meta | hint"
```

### Hand-off contract
- Every quote has all fields filled.
- Misspellings preserved.
- No paraphrasing.
- No quotes that are already in the Facts Log (de-duplication is INTAKE's job, not Synthesis's).

### Implementation
Typically Prompts 1–3 in the prompt sequence. Parallel subagents reading by date range are the most efficient.

---

## Role 2 — SYNTHESIS

### Inputs
- New verbatim quotes from INTAKE (in the format above)
- Existing Findings file
- Existing Open Questions queue

### Outputs
- **Updated Findings file** — new Findings appended, each graded FACT/HYPOTHESIS/SPECULATION.
- **Updated Open Questions queue** — new questions added, each with a falsification rule.
- **A "Findings to promote" list** — existing HYPOTHESES that the new quotes have promoted to FACT.

### Hand-off contract
- Each new Finding includes:
  - Headline claim (1 sentence).
  - Source quote(s) with full provenance.
  - Grade (FACT / HYPOTHESIS / SPECULATION).
  - For HYPOTHESIS: a defined falsification rule.
  - Status note: how many independent sources support it, dates of supports.
- Synthesis NEVER deletes existing Findings or downgrades them. That's AUDIT's job.

### Implementation
Synthesis is typically the orchestrator's job in the parallel-subagent prompts. The orchestrator reads sub-agent outputs and assembles the Findings update.

---

## Role 3 — AUDIT

### Inputs
- Current Findings file (post-Synthesis)
- Findings_Audit.md from the previous audit pass (if any)
- The Facts Log (to verify quotes)

### Outputs
- **Findings_Audit.md** — fresh audit at this moment in time, with each Finding marked 🟢 / 🟡 / 🟠 / 🔴.
- **A "demote / promote / deprecate" diff** — every Finding whose grade or status changed in this audit, with the reason.

### Hand-off contract
- Each Finding's audit row includes:
  - Headline claim.
  - Status (current).
  - Trust ring (audit verdict).
  - Source(s) — quoted directly.
  - Smell test (1–2 sentences on goofing risk).
  - Recommendation (USE / TEST / RETIRE).
- AUDIT never adds new Findings. Only re-grades existing ones.
- AUDIT must check the Facts Log — every Finding's claimed source must actually exist there.

### Implementation
Typically a single agent doing a focused audit pass. **Critical that AUDIT is a different conversation from SYNTHESIS.** Otherwise the auditor inherits the synthesizer's confirmation bias.

If using one human: separate by time (write Findings now, audit them next week).

---

## Role 4 — BACKTEST

### Inputs
- The post-AUDIT Findings file (only audit-passed FACTs and HYPOTHESES; deprecated and 🔴 are excluded)
- The rule-set spec doc (the operationalization of the Findings)
- Ground-truth data adapter

### Outputs
- **Per-event measured results** for every event the rule-set fired on.
- **Aggregate metrics:** hit rate, expectancy, distribution by sub-window / state / asset.
- **Updated Findings status:** HYPOTHESES whose backtest passed → ready for promotion to FACT (after AUDIT confirms).
- **A residual-gap number:** measured metric vs the source's verbatim claim.

### Hand-off contract
- Backtest does NOT modify Findings directly. It produces a recommendation: "Finding NN: backtest passed at X% hit rate over N events; recommend promotion to FACT."
- The actual promotion goes back through AUDIT (so AUDIT is the only gate that grants FACT-grade status).
- Backtest must be reproducible: same config + same data → same numbers.

### Implementation
Typically Prompt 5 (build the engine) + Prompt 6 (orchestration loop). The engine is a Python module; the loop is a multi-iteration sweep over filter candidates.

---

## The closed loop

In production the four agents form a closed loop, not a linear pipeline:

```
   AUDIT promotes a HYPOTHESIS to FACT  (after BACKTEST evidence)
                  │
                  ▼
   The new FACT changes the rule-set spec
                  │
                  ▼
   BACKTEST re-runs with the updated rule set
                  │
                  ▼
   New residual-gap number — closer to or further from {ENTITY}'s claim
                  │
                  ▼
   If still gap: AUDIT identifies which HYPOTHESES are most likely
                 to close it, prioritizes them in OPEN_QUESTIONS
                  │
                  ▼
   INTAKE focuses next pass on those questions
                  │
                  ▼
   SYNTHESIS proposes new Findings or refinements
                  │
                  ▼
   (loop back to AUDIT)
```

The loop terminates when:
1. The residual gap is within 5 pts of the source's claim, OR
2. The corpus is exhausted and no new Findings are emerging, OR
3. The orchestrator decides the rule set is good enough for the use case.

## Why the separation matters

A single agent doing all four roles produces:
- **INTAKE bias:** the agent finds quotes that fit the existing Findings, ignoring contrary evidence.
- **SYNTHESIS overclaiming:** the agent grades their own claims too generously.
- **AUDIT laziness:** the agent doesn't dare downgrade their own previous work.
- **BACKTEST tuning-to-claim:** the agent unconsciously tunes the engine until it matches the source's claim.

Separating the four roles is the discipline that prevents these. Each role has a different incentive:

- INTAKE wants to be thorough (find more, not less).
- SYNTHESIS wants to be coherent (one sensible Finding per cluster of quotes).
- AUDIT wants to be conservative (downgrade unless the evidence is overwhelming).
- BACKTEST wants to be reproducible (run the rules as written, even if they look wrong).

When the four are in tension, the system is healthy. When they all agree by default, you have a single agent in disguise.

## Practical mapping

In a typical Claude Code project, the four roles map to:

| Role | Implementation |
|---|---|
| INTAKE | Prompts 1, 2, 3 in the prompt sequence. Parallel subagents per date range or per artifact. |
| SYNTHESIS | The orchestrator within each Prompt 1/2/3 run. |
| AUDIT | A separate human-driven pass on the Findings. The `Findings_Audit.md` file. |
| BACKTEST | Prompts 5 and 6. The Python engine. |

## Variations

- **Single-investigator startups:** all four roles played by the same human, but separated by time (different sessions, different days, with explicit context-switching).
- **Pair-investigation:** two humans, each owning two roles. Common pairing: one does INTAKE+SYNTHESIS, the other does AUDIT+BACKTEST. Strong because audit and backtest are the skeptical roles.
- **Multi-agent automation:** four separate Claude Code conversations, one per role. The most rigorous but the most expensive. Best when the investigation is long-running.
