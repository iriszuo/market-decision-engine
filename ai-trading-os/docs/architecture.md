# Architecture

## Components

### MODE A: Daily Planning Engine

MODE A runs once per trading day. It analyzes market structure and produces 1 to 5 trade candidates. It may define entry conditions, invalidation levels, risk, and next-day posture, but it must not make execution decisions.

Output: `state/plan.json`

### MODE B: Intraday Optimization Engine

MODE B reads the daily plan and current market conditions. It can strengthen, delay, cancel, or risk-adjust planned candidates. It may add at most one new opportunity.

Output: `state/adjustment.json`

### State Merger

The merger combines MODE A and MODE B into final executable state.

Output: `state/final_state.json`

Merge priority:

1. Start from MODE A candidates.
2. Apply MODE B candidate adjustments by `id`.
3. Add at most one MODE B opportunity.
4. Recalculate summary risk.
5. Emit sorted deterministic JSON.

### Risk Calculator

The risk calculator enforces portfolio risk boundaries:

- default single trade risk: 3% to 6%
- maximum single trade risk: 10%
- aggressive risk only when explicitly justified by market regime alignment

### Signal Validator

The signal validator checks that every candidate has required execution fields:

- entry price
- invalidation price
- stop logic
- expected risk/reward
- portfolio risk

## State Immutability

State is immutable by trading date. `plan.json` is generated once per day. `adjustment.json` may be refreshed during the session, but it must refer to the same `trading_date`. `final_state.json` is derived and must not be edited manually.

## Operational Boundary

No component sends orders to a broker. The final output is a human-readable, schema-bound manual execution state.
