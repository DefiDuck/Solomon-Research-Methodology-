# Backtest skeleton

The structural shell of a Solomon-method backtest engine. Copy this folder into your project, fill in the rule definitions for your domain, and you have a runnable engine.

## What this skeleton provides

- The 7-module structure (data, primitives, state, selector, simulate, backtest, report).
- Function signatures and dataclass interfaces.
- The orchestration loop in `backtest.py` that ties them together.
- The reporting layer (per-event CSV + aggregate JSON + Markdown).
- A CLI entry point.

## What this skeleton does NOT provide

- **Any actual rule logic.** Every function body is `# TODO: define for your domain`.
- **Any data adapter.** `data.py` has stub fetcher signatures. Plug in your domain's data source.
- **Any unit-size table.** `data.py` has a placeholder dict. Fill in the actual sizes for your assets.
- **Any sub-window definitions.** `backtest.py` has a placeholder dict. Fill in the actual session times.

The point is: the skeleton enforces the **shape** of a Solomon-method engine. The shape is what makes it Solomon-method-compliant. The content is yours.

## Module map

| Module | Implements | Phase 5 prompt section |
|---|---|---|
| `data.py` | Ground-truth data fetching with cache | Engine API → `fetch_data` |
| `primitives.py` | Validates {SIGNAL_FEATURE}s per the primitive rule | Engine API → `find_validated_primitives` |
| `state.py` | Classifies state per the state rule | Engine API → `classify_state` |
| `selector.py` | Picks {ACTIVE_PAIR} and computes {MIDPOINT} | Engine API → `find_active_pair`, `midpoint` |
| `simulate.py` | Walks one event forward with {EXIT_RULE} primary + boundary backstop | Engine API → `simulate_event` |
| `backtest.py` | Top-level loop that ties all of the above together | Engine API → `run_backtest` |
| `report.py` | Writes per-event CSV + aggregate JSON + Markdown | Engine API → `write_report` |

## How to fill in the placeholders

For each `# TODO` in the source:

1. Look at the Finding(s) the rule comes from (cited in the docstring).
2. Read the verbatim source quote in your Facts Log.
3. Implement the rule **as documented**, not as you intuit it should be. If the docs say "N same-type events," check exactly N same-type events, not "approximately."
4. Add a docstring linking back to the Finding ID and the source quote.
5. Add a unit test that locks in the rule's behavior on a synthetic example.

When you've filled in all the `# TODO`s, the engine is your engine.

## Setup

```bash
python -m pip install -r requirements.txt
```

Then implement your data adapter in `solomon_engine/data.py` and run:

```bash
python cli.py --asset YOUR_ASSET --granularity YOUR_GRANULARITY --run-id smoke_test
```

## Backwards compatibility discipline

When extending the engine in Phase 2 (orchestration loop), follow the rule:

> Any new filter, parameter, or option must default to "off." Re-running the original Phase 1 config after the extension must produce identical metrics.

This is what lets you sweep filters without losing the ability to reproduce baselines. Copy this discipline; do not skip it.
