"""Signal validation for execution-ready trade candidates."""

from __future__ import annotations

from risk_calculator import validate_trade_risk

REQUIRED_FIELDS = {
    "direction",
    "id",
    "entry",
    "expected_rr",
    "invalidation_price",
    "market",
    "portfolio_risk_pct",
    "sector_tags",
    "status",
    "stop_logic",
    "symbol",
    "thesis",
}


def validate_candidate(candidate: dict) -> None:
    missing = sorted(REQUIRED_FIELDS - set(candidate))
    if missing:
        raise ValueError(f"{candidate.get('id', '<unknown>')}: missing {missing}")

    entry = candidate["entry"]
    if not isinstance(entry, dict) or "trigger_price" not in entry:
        raise ValueError(f"{candidate['id']}: entry.trigger_price is required")

    if float(entry["trigger_price"]) <= 0:
        raise ValueError(f"{candidate['id']}: entry trigger must be positive")
    if float(candidate["invalidation_price"]) <= 0:
        raise ValueError(f"{candidate['id']}: invalidation price must be positive")
    if float(candidate["expected_rr"]) <= 0:
        raise ValueError(f"{candidate['id']}: expected_rr must be positive")

    validate_trade_risk(candidate)


def validate_candidates(candidates: list[dict]) -> None:
    ids: set[str] = set()
    for candidate in candidates:
        candidate_id = candidate.get("id")
        if candidate_id in ids:
            raise ValueError(f"duplicate candidate id: {candidate_id}")
        ids.add(candidate_id)
        validate_candidate(candidate)
