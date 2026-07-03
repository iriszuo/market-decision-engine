"""Deterministic state merger for AI Trading OS."""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = ENGINE_DIR.parent
TOOLS_DIR = PROJECT_DIR / "tools"
sys.path.insert(0, str(TOOLS_DIR))

from json_utils import read_json, write_json_atomic
from risk_calculator import MAX_SINGLE_TRADE_RISK_PCT, total_active_risk_pct
from signal_validator import validate_candidates


def deep_merge(base: dict, updates: dict) -> dict:
    merged = copy.deepcopy(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def merge_state(plan: dict, adjustment: dict, plan_path: str, adjustment_path: str) -> dict:
    if plan.get("mode") != "A":
        raise ValueError("plan mode must be A")
    if adjustment.get("mode") != "B":
        raise ValueError("adjustment mode must be B")
    if plan.get("trading_date") != adjustment.get("trading_date"):
        raise ValueError("plan and adjustment trading_date must match")
    if adjustment.get("source_plan_date") != plan.get("trading_date"):
        raise ValueError("adjustment source_plan_date must match plan trading_date")

    candidates_by_id = {candidate["id"]: copy.deepcopy(candidate) for candidate in plan["candidates"]}
    added_opportunities = 0

    for item in adjustment.get("adjustments", []):
        action = item["action"]

        if action == "add_opportunity":
            added_opportunities += 1
            if added_opportunities > 1:
                raise ValueError("MODE B may add at most one opportunity")
            candidate = copy.deepcopy(item["new_candidate"])
            candidates_by_id[candidate["id"]] = candidate
            continue

        candidate_id = item["candidate_id"]
        if candidate_id not in candidates_by_id:
            raise ValueError(f"unknown candidate_id in adjustment: {candidate_id}")

        updates = copy.deepcopy(item.get("updates", {}))
        if action == "cancel_trade":
            updates["status"] = "cancelled"
        elif action == "delay_entry":
            updates.setdefault("status", "delayed")
        elif action == "strengthen_entry":
            updates.setdefault("status", "strengthened")

        if action == "increase_risk":
            alignment = item.get("market_regime_alignment")
            if alignment != "strong":
                raise ValueError("increase_risk requires strong market_regime_alignment")

        candidates_by_id[candidate_id] = deep_merge(candidates_by_id[candidate_id], updates)

    candidates = sorted(candidates_by_id.values(), key=lambda candidate: candidate["id"])
    for candidate in candidates:
        candidate["manual_execution_only"] = True

    validate_candidates(candidates)

    return {
        "candidates": candidates,
        "generated_at": adjustment["generated_at"],
        "market": plan["market"],
        "market_regime": plan["market_regime"],
        "mode": "FINAL",
        "risk_summary": {
            "max_single_trade_risk_pct": MAX_SINGLE_TRADE_RISK_PCT,
            "total_active_risk_pct": total_active_risk_pct(candidates),
        },
        "source_files": {
            "adjustment": adjustment_path,
            "plan": plan_path,
        },
        "trading_date": plan["trading_date"],
        "version": "1.0",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge MODE A plan and MODE B adjustment state.")
    parser.add_argument("--plan", default=str(PROJECT_DIR / "state" / "plan.json"))
    parser.add_argument("--adjustment", default=str(PROJECT_DIR / "state" / "adjustment.json"))
    parser.add_argument("--output", default=str(PROJECT_DIR / "state" / "final_state.json"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    plan = read_json(args.plan)
    adjustment = read_json(args.adjustment)
    final_state = merge_state(plan, adjustment, args.plan, args.adjustment)
    write_json_atomic(args.output, final_state)


if __name__ == "__main__":
    main()
