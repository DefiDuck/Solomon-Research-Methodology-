# Prompt 7 — Live event receiver

**Copy everything below this line into Claude Code.**

---

You are extending the {RULE_NAME} engine with a live capture component. The historical corpus is finite. Once the engine is validated against the historical sample (Prompts 5 and 6), the next way to grow N is to capture **live events as they fire** — every time the rule set predicts an actionable event in real-time, log it; every time {ENTITY} themselves posts a live event, also log it. After enough live events accumulate (typically 30+ days of capture), you re-run the orchestration loop on the union of historical + live data and the residual gap to {ENTITY}'s claim shrinks again.

This prompt builds that receiver and integrates it with the engine.

**You are in the project root.** Read these files first:
1. `engine/runs/PHASE_2_SUMMARY.md` — the validated configuration from Phase 2
2. `findings/RULE_SET.md` — the rule predicates you'll evaluate live
3. The documentation for whatever real-time signal source your domain has (webhook spec, poll endpoint, alert API, RSS feed)

## Architecture

The receiver is a long-running service with three components:

```
   ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
   │  signal source   │───▶│   ingest layer   │───▶│  storage layer   │
   │                  │    │  (push or poll)  │    │  (append-only)   │
   │  webhook /       │    │                  │    │                  │
   │  poll endpoint / │    │  validates,      │    │  live_events.csv │
   │  alert API       │    │  parses, dedups  │    │  + cache         │
   └──────────────────┘    └──────────────────┘    └──────────────────┘
                                                              │
                                                              ▼
                                              ┌──────────────────────────┐
                                              │  re-run integration      │
                                              │                          │
                                              │  weekly: run validated   │
                                              │  config against new      │
                                              │  events, compare to      │
                                              │  historical metric       │
                                              └──────────────────────────┘
```

## Implementation modes

There are two ways to capture live events. Implement whichever your signal source supports.

### Mode A — Push (webhook)

If your signal source supports webhooks (alerts platform with HTTP-POST hooks, chat platform bot interface, etc.), build a small Flask/FastAPI server that:

1. Listens on a public HTTPS endpoint (use a tunnel like Cloudflare Tunnel or ngrok if your machine isn't internet-facing).
2. Accepts a JSON payload with the event's structured fields.
3. Validates the payload signature against a shared secret (all reputable signal sources sign their webhooks).
4. Appends one row to `engine/runs/live_events.csv` with the schema below.
5. Optionally fires a push notification to the user (Pushover, Telegram, Discord webhook).

The endpoint URL goes into the signal source's webhook configuration. The signal source posts every time a rule predicate fires.

### Mode B — Pull (polling)

If your signal source only exposes a query API:

1. Build a polling loop that runs every N seconds (rate-limit-aware — typically 30 sec to 5 min depending on the API).
2. Each poll, query the API for new events since the last successful poll timestamp.
3. Append rows to `engine/runs/live_events.csv` with the schema below.
4. Persist `last_poll_timestamp` to disk after each successful append, so the loop survives restarts without losing or duplicating events.
5. Run the loop under `systemd` / `pm2` / `nohup` / equivalent so it stays up.

### Hybrid (recommended for higher fidelity)

Some domains let you do both: webhook for {ENTITY}-fired alerts (high-trust, fast) and poll for general background events (broader coverage). Run both; deduplicate by `event_id` when present.

## Event schema

Every captured event lands in `live_events.csv` with these columns:

```
timestamp_received   ← when your receiver saw the event (your wall clock)
timestamp_event      ← when the event actually fired (from the payload, if available)
source               ← which channel (webhook URL, poll endpoint, alert ID)
event_id             ← stable identifier for dedup (hash of payload if not provided)
asset                ← which {ASSET} this event references
parsed_entry         ← the {ENTRY_RULE} value the event encodes (or null)
parsed_window        ← which {WINDOW} the event occurred in
parsed_state         ← the state classification at event time
raw_payload          ← the raw JSON the source posted, gzipped if large
notes                ← any free-text annotation, e.g. {ENTITY}'s own caption
```

CSV is the right format here for two reasons: trivial to append in any language without serialization friction, and easy to load into pandas later for re-runs.

## Re-run integration

The receiver alone is not the deliverable. The receiver feeds the **re-run loop**, which is what closes the residual gap.

After the receiver has accumulated ≥30 events (or ≥4 weeks of capture, whichever comes first):

1. Fetch ground-truth data for the captured event timestamps.
2. Run the validated Phase 2 backtest config against this new sample.
3. Compute live-only metrics. Compare to the historical metrics from Phase 2.
4. **If they match within 3 pts:** the validated rules generalize forward in time. The framework is durable.
5. **If they diverge by >5 pts:** either the source's setup has shifted (re-investigate), or the historical sample was over-fit (re-run with broader filters).

Re-run integration runs as a weekly cron job. Output goes to `engine/runs/live_events_log.md` (auto-updated).

## Operational discipline

- **No real-world actions.** This receiver captures and logs. Even if the signal source allows you to act on the event, this prompt's job is logging only. Acting is downstream.
- **No personal data retention.** If the live channel has multi-user content, scrub user identifiers at intake. Hash usernames before they hit storage.
- **Document failure modes.** If the webhook server crashes or the polling loop breaks, you should be able to detect within 1 hour (uptime monitoring) and recover without losing events (replay from the source's recent-events endpoint).
- **Rate-limit awareness.** Respect the signal source's rate limits. Most alert APIs cap at 1 req/sec per endpoint; webhook receivers should accept ≤100 req/sec without dropping.

## Deliverable

`engine/runs/live_events_log.md` — auto-generated, refreshed weekly by the re-run cron. Format:

```
# Live Event Log
Receiver started: YYYY-MM-DD
Last event captured: YYYY-MM-DD HH:MM:SS
Total events: N
Last re-run: YYYY-MM-DD

## Recent events (last 30)
| timestamp | source | asset | parsed_entry | window | notes |
|---|---|---|---|---|---|

## Re-run analysis (refreshed weekly)
- Live-only hit rate: X% (n=Y)
- Historical hit rate (Phase 2): Z%
- Δ: ±W pts
- Drift verdict: STABLE / DRIFTING / UNCERTAIN
```

When the receiver is operational and has its first re-run analysis, summarize the integration plan and ask the user whether to extend capture or adjust parameters.

---

## Important rules

- **Time budget:** ~2–4 hours of setup, then ongoing background. The valuable output accrues over weeks.
- **Prefer Mode A (push) over Mode B (poll)** if your signal source supports it. Webhooks are lower latency, lower cost, more reliable.
- **Storage scales linearly.** A receiver running for a year at 10 events/day is ~3.6k events. Plain CSV is fine. No need to over-architect.
- **The receiver is a tool, not the deliverable.** The deliverable is the live-events log + the weekly re-run analysis. The receiver just keeps the data flowing.
