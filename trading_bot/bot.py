"""The bot orchestrator.

Wraps the strategy + risk + backtester behind a small, friendly API and a
paper-trading loop. There is deliberately **no live-money/exchange code** here:
the bot trades on paper so you can validate a strategy before ever risking real
funds. To go live you would implement `_submit_order` against a broker API —
but do that only after thorough backtesting and with money you can afford to
lose.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .backtest import Backtester, BacktestResult, Trade
from .config import Config
from .data import Bar, closes as bar_closes
from .indicators import atr as atr_indicator
from .risk import Bracket, build_bracket, stop_hit, take_profit_hit
from .strategy import Signal, Strategy


@dataclass
class PaperPosition:
    entry_price: float
    quantity: float
    bracket: Bracket
    side: str = "long"


class TradingBot:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.strategy = Strategy(self.config)
        self.cash = self.config.starting_cash
        self.position: Optional[PaperPosition] = None
        self.history: List[Trade] = []
        self._bars: List[Bar] = []

    # --- backtesting ---------------------------------------------------------
    def backtest(self, bars: List[Bar]) -> BacktestResult:
        return Backtester(self.config).run(bars)

    # --- paper trading (incremental / streaming) -----------------------------
    def on_bar(self, bar: Bar) -> Optional[str]:
        """Feed one new bar. Returns a human-readable action, or None.

        Designed to be called in a loop as live bars arrive. Uses only data up
        to the current bar (no look-ahead).
        """
        self._bars.append(bar)
        closes = bar_closes(self._bars)
        states = self.strategy.generate(closes)
        state = states[-1]
        i = len(self._bars) - 1
        cfg = self.config
        action: Optional[str] = None

        # manage open position
        if self.position is not None:
            br = self.position.bracket
            if stop_hit(br, bar.low, bar.high, self.position.side):
                action = self._exit(i, br.stop, "stop-loss (2% rule)")
            elif take_profit_hit(br, bar.low, bar.high, self.position.side):
                action = self._exit(i, br.take_profit, "take-profit")
            elif state.signal == Signal.SELL:
                action = self._exit(i, bar.close, f"signal: {state.reason}")

        # consider new entry when flat
        if self.position is None and state.signal == Signal.BUY:
            atr_series = atr_indicator(
                [b.high for b in self._bars],
                [b.low for b in self._bars],
                closes,
                cfg.atr_period,
            )
            br = build_bracket(
                cfg, equity=self.equity(bar.close), entry=bar.close,
                atr_value=atr_series[-1], side="long",
            )
            cost = br.quantity * bar.close * (1 + cfg.fee_pct)
            if br.quantity > 0 and cost <= self.cash:
                self.cash -= cost
                self.position = PaperPosition(bar.close, br.quantity, br, "long")
                action = (
                    f"BUY {br.quantity:.4f} @ {bar.close:.2f} "
                    f"| stop {br.stop:.2f} (-{cfg.stop_loss_pct*100:.0f}%) "
                    f"target {br.take_profit:.2f} | risk {br.risk_pct_of_equity*100:.2f}% equity"
                )
        return action

    def _exit(self, i: int, price: float, reason: str) -> str:
        assert self.position is not None
        pos = self.position
        cfg = self.config
        proceeds = pos.quantity * price * (1 - cfg.fee_pct)
        pnl = proceeds - pos.quantity * pos.entry_price
        self.cash += proceeds
        self.history.append(
            Trade(
                entry_index=-1,
                entry_price=pos.entry_price,
                exit_index=i,
                exit_price=price,
                quantity=pos.quantity,
                side=pos.side,
                pnl=pnl,
                return_pct=(price / pos.entry_price - 1.0) * 100.0,
                exit_reason=reason,
            )
        )
        self.position = None
        return f"SELL {pos.quantity:.4f} @ {price:.2f} | {reason} | PnL {pnl:+.2f}"

    def equity(self, last_price: Optional[float] = None) -> float:
        eq = self.cash
        if self.position is not None and last_price is not None:
            eq += self.position.quantity * last_price
        return eq
