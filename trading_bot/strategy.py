"""Trading strategy: trend + momentum confirmation.

The "AI" in an algorithmic bot is its decision logic. This strategy keeps that
logic transparent and rule-based (which is auditable and reproducible, unlike a
black box):

ENTER LONG on either of two complementary triggers:
  A) Golden cross — fast EMA crosses *above* slow EMA this bar (a fresh
     uptrend), with RSI not already overbought (don't chase an exhausted move).
  B) Pullback buy — already in an uptrend (fast > slow) and RSI dipped to/under
     `rsi_oversold` and is now turning back up (buy the dip, not the knife).

EXIT LONG when any hold (signal-based; risk.py adds hard stops on top):
  * Trend flips:    fast EMA < slow EMA
  * Overbought:     RSI >= overbought

The bot is long-only by default. Short logic is the mirror image and is gated
behind Config.allow_short.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from .config import Config
from .indicators import ema, rsi


class Signal(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class StrategyState:
    index: int
    price: float
    fast_ema: Optional[float]
    slow_ema: Optional[float]
    rsi: Optional[float]
    signal: Signal
    reason: str


class Strategy:
    def __init__(self, config: Config):
        self.config = config

    def generate(self, closes: List[float]) -> List[StrategyState]:
        """Compute a signal for every bar. No look-ahead: bar i only uses
        information available up to and including bar i."""
        cfg = self.config
        fast = ema(closes, cfg.fast_ema)
        slow = ema(closes, cfg.slow_ema)
        rsis = rsi(closes, cfg.rsi_period)

        states: List[StrategyState] = []
        for i, price in enumerate(closes):
            signal, reason = self._signal_for_bar(i, fast, slow, rsis)
            states.append(
                StrategyState(
                    index=i,
                    price=price,
                    fast_ema=fast[i],
                    slow_ema=slow[i],
                    rsi=rsis[i],
                    signal=signal,
                    reason=reason,
                )
            )
        return states

    def _signal_for_bar(self, i, fast, slow, rsis):
        cfg = self.config
        f, s, r = fast[i], slow[i], rsis[i]
        pf, ps, pr = fast[i - 1], slow[i - 1], rsis[i - 1]
        if None in (f, s, r, pf, ps) or i == 0:
            return Signal.HOLD, "warming up"

        uptrend = f > s
        was_uptrend = pf > ps
        golden_cross = uptrend and not was_uptrend
        death_cross = (not uptrend) and was_uptrend

        # --- exits take priority over entries ---------------------------------
        if death_cross:
            return Signal.SELL, f"trend flip down (EMA{cfg.fast_ema}<{cfg.slow_ema})"
        if r >= cfg.rsi_overbought:
            return Signal.SELL, f"RSI overbought {r:.1f}"

        # --- entry A: golden cross with momentum not yet exhausted ------------
        if golden_cross and r < cfg.rsi_overbought:
            return Signal.BUY, (
                f"golden cross EMA{cfg.fast_ema}>{cfg.slow_ema}, RSI {r:.1f}"
            )

        # --- entry B: pullback inside an established uptrend ------------------
        if uptrend and pr is not None and pr <= cfg.rsi_oversold and r > pr:
            return Signal.BUY, f"uptrend pullback, RSI turning up {pr:.1f}->{r:.1f}"

        # --- optional short on a death cross + falling momentum --------------
        if cfg.allow_short and (not uptrend) and pr is not None and r < pr:
            return Signal.SELL, "short setup: downtrend + RSI rolling over"

        return Signal.HOLD, "no setup"
