"""A library of pre-built strategy templates.

Like pinecode.ai's starter indicators: if you don't have a strategy yet, pick
one of these proven archetypes and tweak it. Each returns a ready-to-generate
:class:`StrategySpec` with sensible risk defaults (2% stop, 2:1 target).
"""

from __future__ import annotations

from typing import Callable, Dict

from .spec import Indicator, Rule, StrategySpec


def ema_crossover(fast: int = 12, slow: int = 26) -> StrategySpec:
    """Golden/death cross: go long when fast EMA crosses above slow EMA."""
    s = StrategySpec(name=f"EMA {fast}/{slow} Crossover")
    s.add(Indicator("emaFast", "ema", length=fast))
    s.add(Indicator("emaSlow", "ema", length=slow))
    s.long_entry = [Rule("emaFast", "crossover", "emaSlow")]
    s.long_exit = [Rule("emaFast", "crossunder", "emaSlow")]
    return s


def rsi_reversion(length: int = 14, oversold: float = 30, overbought: float = 70) -> StrategySpec:
    """Mean reversion: buy oversold, sell overbought."""
    s = StrategySpec(name=f"RSI {length} Reversion")
    s.add(Indicator("rsi", "rsi", length=length))
    s.add(Indicator("osLevel", "const", value=oversold))
    s.add(Indicator("obLevel", "const", value=overbought))
    s.long_entry = [Rule("rsi", "crossover", "osLevel")]
    s.long_exit = [Rule("rsi", "crossover", "obLevel")]
    return s


def ema_rsi_trend(fast: int = 12, slow: int = 26, rsi_len: int = 14) -> StrategySpec:
    """Trend + momentum: long only in an uptrend when RSI turns up from oversold."""
    s = StrategySpec(name="EMA Trend + RSI Pullback")
    s.add(Indicator("emaFast", "ema", length=fast))
    s.add(Indicator("emaSlow", "ema", length=slow))
    s.add(Indicator("rsi", "rsi", length=rsi_len))
    s.add(Indicator("osLevel", "const", value=35))
    s.add(Indicator("obLevel", "const", value=70))
    s.long_entry = [Rule("emaFast", ">", "emaSlow"), Rule("rsi", "crossover", "osLevel")]
    s.long_exit = [Rule("emaFast", "crossunder", "emaSlow"), Rule("rsi", "crossover", "obLevel")]
    return s


def macd_trend(fast: int = 12, slow: int = 26, signal: int = 9) -> StrategySpec:
    """MACD line crossing its signal line."""
    s = StrategySpec(name="MACD Trend")
    s.add(Indicator("macdLine", "macd_line", fast=fast, slow=slow, signal=signal))
    s.add(Indicator("macdSig", "macd_signal", fast=fast, slow=slow, signal=signal))
    s.long_entry = [Rule("macdLine", "crossover", "macdSig")]
    s.long_exit = [Rule("macdLine", "crossunder", "macdSig")]
    return s


def bollinger_breakout(length: int = 20, mult: float = 2.0) -> StrategySpec:
    """Buy a close above the upper Bollinger Band, exit back at the basis."""
    s = StrategySpec(name=f"Bollinger {length} Breakout")
    s.add(Indicator("price", "close", length=1))
    s.add(Indicator("bbUpper", "bb_upper", length=length, mult=mult))
    s.add(Indicator("bbBasis", "bb_basis", length=length, mult=mult))
    s.long_entry = [Rule("price", "crossover", "bbUpper")]
    s.long_exit = [Rule("price", "crossunder", "bbBasis")]
    return s


TEMPLATES: Dict[str, Callable[[], StrategySpec]] = {
    "ema_crossover": ema_crossover,
    "rsi_reversion": rsi_reversion,
    "ema_rsi_trend": ema_rsi_trend,
    "macd_trend": macd_trend,
    "bollinger_breakout": bollinger_breakout,
}


def get(name: str) -> StrategySpec:
    if name not in TEMPLATES:
        raise KeyError(f"unknown template {name!r}; available: {sorted(TEMPLATES)}")
    return TEMPLATES[name]()
