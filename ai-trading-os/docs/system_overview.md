# System Overview

AI Trading OS is a trading decision operating system built around immutable daily state.

It separates planning, intraday adjustment, and execution:

- MODE A generates the daily plan.
- MODE B updates the plan based on intraday conditions.
- The state merger produces final executable state.
- A human performs any trade manually.

The engine is intentionally narrow. It protects consistency, risk limits, and execution clarity rather than trying to predict markets directly.

## Trading State Machine

```text
MODE A daily plan -> MODE B adjustment -> merged final state -> manual execution
```

## Source of Truth

GitHub-hosted JSON files are the only persisted state. Local files may be used for development, but the canonical state model is:

- `plan.json`: one daily plan per trading date
- `adjustment.json`: intraday updates for the same trading date
- `final_state.json`: derived state created by the merger

`final_state.json` is reproducible from `plan.json` and `adjustment.json`.

## Trading Scope

The system supports A-share and US-share workflows through configuration fields in state. It does not assume automated execution and does not require broker credentials.

## Determinism

All generated state must be:

- structured JSON
- schema-valid
- reproducible from explicit inputs
- free of hidden execution actions
