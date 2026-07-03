# Execution Flow

## 1. Create Daily Plan

Run MODE A before the trading session. The output must be JSON only and must validate against `schemas/plan_schema.json`.

Rules:

- generate 1 to 5 candidates
- use price-based entry conditions
- include invalidation levels
- include T+1-aware stop logic
- include expected risk/reward
- do not make execution decisions

## 2. Create Intraday Adjustment

Run MODE B during the session after reading the current `plan.json`.

Allowed actions:

- `strengthen_entry`
- `delay_entry`
- `cancel_trade`
- `increase_risk`
- `reduce_risk`
- `add_opportunity`

MODE B must not regenerate the full portfolio.

## 3. Merge State

Run the merger:

```bash
python engine/state_merger.py --plan state/plan.json --adjustment state/adjustment.json --output state/final_state.json
```

The final state follows strict priority:

```text
MODE B overrides MODE A
```

## 4. Manual Execution

The human operator reviews `final_state.json` and decides whether to trade. The system provides structured instructions only. It does not place orders.

## 5. Logging

Daily decisions may be archived under `logs/daily/`. Completed manual trades may be archived under `logs/trades/`. Logs should reference the `trading_date` and candidate `id`.
