# AI Trading OS

AI Trading OS is a state-driven trading decision engine. It is not a trading bot, brokerage connector, backtester, or stock picker.

The system produces deterministic, structured decision state for manual human execution:

1. MODE A creates one daily plan.
2. MODE B adjusts the plan during the session.
3. The merger derives the final state.
4. A human reviews and executes trades manually.

GitHub JSON files are the source of truth for persisted state.

## Core State Files

- `state/plan.json`: MODE A daily plan. Generated once per trading day.
- `state/adjustment.json`: MODE B intraday adjustment.
- `state/final_state.json`: derived state. Never edit manually.

Merge priority is strict: MODE B overrides MODE A.

## Execution Boundary

This repository does not place orders. It emits manual execution instructions only. Every trade candidate must include entry price, invalidation price, T+1-aware stop logic, expected risk/reward, and portfolio risk.

## Quick Start

Validate and merge the sample state:

```bash
python ai-trading-os/engine/state_merger.py \
  --plan ai-trading-os/examples/sample_plan.json \
  --adjustment ai-trading-os/examples/sample_adjustment.json \
  --output ai-trading-os/state/final_state.json
```

The merger is deterministic and writes stable, sorted JSON.

## Repository Layout

- `docs/`: system design and execution flow
- `prompts/`: prompts for MODE A, MODE B, and controller usage
- `schemas/`: JSON Schema contracts for plan, adjustment, and execution state
- `engine/`: deterministic state and risk utilities
- `tools/`: JSON and GitHub state helpers
- `state/`: current persisted state
- `logs/`: daily and trade logs
- `examples/`: sample inputs

## Non-Goals

- No automated brokerage execution
- No live order routing
- No portfolio rebalancing automation
- No backtest framework
- No discretionary free-form trade output
