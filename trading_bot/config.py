"""Configuration for the trading bot.

All tunable parameters live here so the strategy and risk rules are easy to
audit and adjust. Defaults are intentionally conservative.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field


@dataclass
class Config:
    # --- Strategy parameters -------------------------------------------------
    fast_ema: int = 12          # fast trend filter
    slow_ema: int = 26          # slow trend filter
    rsi_period: int = 14        # momentum lookback
    rsi_oversold: float = 35.0  # below -> momentum supports a long
    rsi_overbought: float = 70.0  # above -> exit / avoid new longs
    atr_period: int = 14        # volatility lookback (for adaptive stops)

    # --- Risk management -----------------------------------------------------
    # The single most important rule in this bot: never lose more than
    # `stop_loss_pct` of the *entry price* on a position, and never risk more
    # than `risk_per_trade` of *account equity* on any single trade.
    stop_loss_pct: float = 0.02         # hard 2% stop loss (the "2% loss" rule)
    take_profit_pct: float = 0.04       # default 2:1 reward:risk target
    risk_per_trade: float = 0.01        # risk 1% of equity per trade
    max_position_pct: float = 1.0       # cap position at 100% of equity
    use_atr_stops: bool = False         # if True, widen stops by volatility
    atr_stop_mult: float = 2.0          # ATR multiplier when use_atr_stops

    # --- Account / costs -----------------------------------------------------
    starting_cash: float = 10_000.0
    fee_pct: float = 0.001              # 0.1% per side (taker fee)
    slippage_pct: float = 0.0005        # 0.05% adverse fill assumption

    # --- Misc ----------------------------------------------------------------
    allow_short: bool = False           # long-only by default (safer)
    symbol: str = "DEMO"

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.fast_ema >= self.slow_ema:
            raise ValueError("fast_ema must be < slow_ema")
        if not (0 < self.stop_loss_pct < 1):
            raise ValueError("stop_loss_pct must be between 0 and 1")
        if not (0 < self.risk_per_trade <= 1):
            raise ValueError("risk_per_trade must be between 0 and 1")
        if self.take_profit_pct <= 0:
            raise ValueError("take_profit_pct must be > 0")
        for name in ("fast_ema", "slow_ema", "rsi_period", "atr_period"):
            if getattr(self, name) < 1:
                raise ValueError(f"{name} must be >= 1")

    def to_dict(self) -> dict:
        return asdict(self)
