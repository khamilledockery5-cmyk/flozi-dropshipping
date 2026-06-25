"""Risk management — the part that protects capital.

Two rules enforced here:

1. **Hard 2% stop loss.** Every long position carries a stop at
   `entry * (1 - stop_loss_pct)`. If price trades through it, the position is
   closed, capping the loss on that trade. This is the "2% loss" rule.

2. **Fixed fractional position sizing.** We never bet the whole account on one
   idea. Size is chosen so that *if the stop is hit*, the loss equals
   `risk_per_trade` of current equity (default 1%). That decouples "how much do
   I lose if I'm wrong" from "how big is the position".

Optionally stops can be widened by volatility (ATR) so a normally-noisy market
doesn't stop you out prematurely — but the position is then sized smaller to
keep the dollar risk constant.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .config import Config


@dataclass
class Bracket:
    entry: float
    stop: float
    take_profit: float
    quantity: float
    risk_amount: float       # cash at risk if stop is hit
    risk_pct_of_equity: float


def stop_distance(config: Config, entry: float, atr_value: Optional[float]) -> float:
    """Absolute price distance from entry to stop."""
    pct_stop = entry * config.stop_loss_pct
    if config.use_atr_stops and atr_value:
        return max(pct_stop, atr_value * config.atr_stop_mult)
    return pct_stop


def build_bracket(
    config: Config,
    equity: float,
    entry: float,
    atr_value: Optional[float] = None,
    side: str = "long",
) -> Bracket:
    """Size a position and attach stop / take-profit levels.

    Quantity is the largest size whose stop-out loss does not exceed
    `risk_per_trade * equity`, also capped by `max_position_pct` of equity.
    """
    if entry <= 0:
        raise ValueError("entry price must be positive")
    dist = stop_distance(config, entry, atr_value)
    if dist <= 0:
        raise ValueError("stop distance must be positive")

    risk_budget = equity * config.risk_per_trade
    qty_by_risk = risk_budget / dist
    qty_by_cap = (equity * config.max_position_pct) / entry
    quantity = max(0.0, min(qty_by_risk, qty_by_cap))

    if side == "long":
        stop = entry - dist
        take = entry + entry * config.take_profit_pct
    else:  # short
        stop = entry + dist
        take = entry - entry * config.take_profit_pct

    risk_amount = quantity * dist
    return Bracket(
        entry=entry,
        stop=stop,
        take_profit=take,
        quantity=quantity,
        risk_amount=risk_amount,
        risk_pct_of_equity=(risk_amount / equity) if equity else 0.0,
    )


def stop_hit(bracket: Bracket, low: float, high: float, side: str = "long") -> bool:
    if side == "long":
        return low <= bracket.stop
    return high >= bracket.stop


def take_profit_hit(bracket: Bracket, low: float, high: float, side: str = "long") -> bool:
    if side == "long":
        return high >= bracket.take_profit
    return low <= bracket.take_profit
