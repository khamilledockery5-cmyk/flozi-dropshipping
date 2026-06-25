"""Flozi Trading Bot.

A dependency-free algorithmic trading bot with a trend + momentum strategy
and strict risk management: every trade risks a fixed % of equity and is
protected by a hard 2% stop loss.

Modules
-------
- indicators : EMA / RSI / ATR (pure Python)
- strategy   : turns indicators into BUY / SELL / HOLD signals
- risk       : position sizing + stop-loss / take-profit logic
- backtest   : historical simulation with performance stats
- bot        : the orchestrator (backtest or paper-trading loop)
- data       : CSV loader + offline synthetic price generator
"""

__version__ = "1.0.0"

from .config import Config
from .strategy import Signal, Strategy
from .backtest import Backtester, BacktestResult

__all__ = [
    "Config",
    "Signal",
    "Strategy",
    "Backtester",
    "BacktestResult",
    "__version__",
]
