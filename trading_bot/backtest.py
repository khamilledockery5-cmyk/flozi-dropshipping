"""Event-driven backtester.

Walks the bars one at a time, asks the strategy for a signal, and manages a
single position with the risk module's bracket (stop + take-profit). Intrabar
stops/targets are checked against each bar's high/low *before* acting on the
new signal, so the hard 2% stop is honored even on gap-down bars.

Fills include a configurable fee and slippage so results aren't fantasy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .config import Config
from .data import Bar
from .indicators import atr as atr_indicator
from .risk import Bracket, build_bracket, stop_hit, take_profit_hit
from .strategy import Signal, Strategy


@dataclass
class Trade:
    entry_index: int
    entry_price: float
    exit_index: Optional[int] = None
    exit_price: Optional[float] = None
    quantity: float = 0.0
    side: str = "long"
    pnl: float = 0.0
    return_pct: float = 0.0
    exit_reason: str = ""

    @property
    def is_open(self) -> bool:
        return self.exit_index is None


@dataclass
class BacktestResult:
    config: Config
    trades: List[Trade]
    equity_curve: List[float]
    starting_equity: float
    ending_equity: float

    # --- performance stats ---------------------------------------------------
    @property
    def total_return_pct(self) -> float:
        if self.starting_equity == 0:
            return 0.0
        return (self.ending_equity / self.starting_equity - 1.0) * 100.0

    @property
    def closed_trades(self) -> List[Trade]:
        return [t for t in self.trades if not t.is_open]

    @property
    def num_trades(self) -> int:
        return len(self.closed_trades)

    @property
    def wins(self) -> List[Trade]:
        return [t for t in self.closed_trades if t.pnl > 0]

    @property
    def losses(self) -> List[Trade]:
        return [t for t in self.closed_trades if t.pnl <= 0]

    @property
    def win_rate(self) -> float:
        n = self.num_trades
        return (len(self.wins) / n * 100.0) if n else 0.0

    @property
    def profit_factor(self) -> float:
        gross_win = sum(t.pnl for t in self.wins)
        gross_loss = abs(sum(t.pnl for t in self.losses))
        if gross_loss == 0:
            return float("inf") if gross_win > 0 else 0.0
        return gross_win / gross_loss

    @property
    def max_drawdown_pct(self) -> float:
        peak = self.equity_curve[0] if self.equity_curve else 0.0
        max_dd = 0.0
        for v in self.equity_curve:
            peak = max(peak, v)
            if peak > 0:
                dd = (peak - v) / peak
                max_dd = max(max_dd, dd)
        return max_dd * 100.0

    @property
    def worst_trade_pct(self) -> float:
        return min((t.return_pct for t in self.closed_trades), default=0.0)

    def summary(self) -> str:
        lines = [
            f"Symbol:           {self.config.symbol}",
            f"Starting equity:  ${self.starting_equity:,.2f}",
            f"Ending equity:    ${self.ending_equity:,.2f}",
            f"Total return:     {self.total_return_pct:+.2f}%",
            f"Max drawdown:     {self.max_drawdown_pct:.2f}%",
            f"Trades:           {self.num_trades}",
            f"Win rate:         {self.win_rate:.1f}%",
            f"Profit factor:    {self.profit_factor:.2f}",
            f"Worst trade:      {self.worst_trade_pct:+.2f}%",
        ]
        return "\n".join(lines)


class Backtester:
    def __init__(self, config: Config):
        self.config = config
        self.strategy = Strategy(config)

    def run(self, bars: List[Bar]) -> BacktestResult:
        cfg = self.config
        closes = [b.close for b in bars]
        states = self.strategy.generate(closes)
        atr_series = atr_indicator(
            [b.high for b in bars],
            [b.low for b in bars],
            closes,
            cfg.atr_period,
        )

        cash = cfg.starting_cash
        equity = cash
        position: Optional[Trade] = None
        bracket: Optional[Bracket] = None
        trades: List[Trade] = []
        equity_curve: List[float] = []

        for i, bar in enumerate(bars):
            # 1) Manage an open position first (risk before reward).
            if position is not None and bracket is not None:
                exit_price = None
                reason = ""
                # Stop checked before target; on a bar that hits both, assume
                # the worse (stop) filled first — conservative accounting.
                if stop_hit(bracket, bar.low, bar.high, position.side):
                    exit_price = bracket.stop
                    reason = "stop-loss"
                elif take_profit_hit(bracket, bar.low, bar.high, position.side):
                    exit_price = bracket.take_profit
                    reason = "take-profit"
                elif states[i].signal == Signal.SELL and position.side == "long":
                    exit_price = bar.close
                    reason = f"signal: {states[i].reason}"

                if exit_price is not None:
                    cash = self._close(position, bracket, i, exit_price, reason, cash)
                    trades.append(position)
                    position, bracket = None, None

            # 2) Look for a new entry only when flat.
            if position is None and states[i].signal == Signal.BUY:
                fill = self._apply_costs(bar.close, buying=True)
                bracket = build_bracket(
                    cfg, equity=cash, entry=fill, atr_value=atr_series[i], side="long"
                )
                if bracket.quantity > 0:
                    cost = bracket.quantity * fill * (1 + cfg.fee_pct)
                    if cost <= cash:
                        cash -= cost
                        position = Trade(
                            entry_index=i,
                            entry_price=fill,
                            quantity=bracket.quantity,
                            side="long",
                        )
                    else:
                        bracket = None

            # 3) Mark-to-market equity for the curve.
            mtm = cash
            if position is not None:
                mtm += position.quantity * bar.close
            equity = mtm
            equity_curve.append(equity)

        # Close any position still open at the final bar.
        if position is not None and bracket is not None:
            last = len(bars) - 1
            cash = self._close(
                position, bracket, last, bars[last].close, "end-of-data", cash
            )
            trades.append(position)
            equity_curve[-1] = cash

        return BacktestResult(
            config=cfg,
            trades=trades,
            equity_curve=equity_curve,
            starting_equity=cfg.starting_cash,
            ending_equity=equity_curve[-1] if equity_curve else cfg.starting_cash,
        )

    # --- helpers -------------------------------------------------------------
    def _apply_costs(self, price: float, buying: bool) -> float:
        """Adverse slippage: pay up when buying, receive less when selling."""
        slip = self.config.slippage_pct
        return price * (1 + slip) if buying else price * (1 - slip)

    def _close(self, trade, bracket, i, raw_exit, reason, cash) -> float:
        cfg = self.config
        exit_fill = self._apply_costs(raw_exit, buying=False)
        proceeds = trade.quantity * exit_fill * (1 - cfg.fee_pct)
        cost_basis = trade.quantity * trade.entry_price
        trade.exit_index = i
        trade.exit_price = exit_fill
        trade.exit_reason = reason
        trade.pnl = proceeds - cost_basis
        trade.return_pct = (
            (exit_fill / trade.entry_price - 1.0) * 100.0 if trade.entry_price else 0.0
        )
        return cash + proceeds
