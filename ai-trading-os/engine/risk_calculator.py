"""Risk helpers for AI Trading OS."""

from __future__ import annotations

MAX_SINGLE_TRADE_RISK_PCT = 10.0
DEFAULT_RISK_MIN_PCT = 3.0
DEFAULT_RISK_MAX_PCT = 6.0


def validate_trade_risk(candidate: dict) -> None:
    """Raise ValueError when a candidate violates risk boundaries."""
    risk = float(candidate.get("portfolio_risk_pct", -1))
    if risk < 0:
        raise ValueError(f"{candidate.get('id', '<unknown>')}: risk cannot be negative")
    if risk > MAX_SINGLE_TRADE_RISK_PCT:
        raise ValueError(
            f"{candidate.get('id', '<unknown>')}: risk {risk}% exceeds "
            f"{MAX_SINGLE_TRADE_RISK_PCT}% max"
        )


def total_active_risk_pct(candidates: list[dict]) -> float:
    """Return total risk for non-cancelled candidates."""
    total = 0.0
    for candidate in candidates:
        if candidate.get("status") != "cancelled":
            validate_trade_risk(candidate)
            total += float(candidate.get("portfolio_risk_pct", 0))
    return round(total, 4)


def is_aggressive_risk(candidate: dict) -> bool:
    """Return true when candidate risk is above the default range."""
    return float(candidate.get("portfolio_risk_pct", 0)) > DEFAULT_RISK_MAX_PCT
