"""Offline natural-language → :class:`StrategySpec` parser.

A dependency-free keyword parser so PineForge produces a real strategy even
without an API key. It recognizes the common building blocks — EMA/SMA
crossovers, RSI thresholds, MACD, Bollinger breakouts — plus risk phrases like
"2% stop loss" and "risk 1%". For free-form descriptions it can't model, use
the Claude-powered :mod:`pineforge.ai` layer instead.
"""

from __future__ import annotations

import re
from typing import List, Optional

from .spec import Indicator, Rule, StrategySpec


def _find_pct(text: str, *keywords: str, default: Optional[float] = None) -> Optional[float]:
    """Find a percentage associated with any of `keywords` (either order)."""
    for kw in keywords:
        # "2% stop loss" / "stop loss of 2%" / "stop loss 2 percent"
        for pat in (
            rf"(\d+(?:\.\d+)?)\s*%?\s*{kw}",
            rf"{kw}[^\d]{{0,15}}(\d+(?:\.\d+)?)\s*(?:%|percent)",
        ):
            m = re.search(pat, text)
            if m:
                return float(m.group(1))
    return default


def _ma_lengths(text: str, word: str) -> List[int]:
    """Extract lengths like '50 ema', 'ema(200)', '12/26 ema'."""
    lengths: List[int] = []
    for m in re.finditer(rf"(\d+)\s*(?:/|and|,)?\s*(\d+)?\s*{word}", text):
        lengths.append(int(m.group(1)))
        if m.group(2):
            lengths.append(int(m.group(2)))
    for m in re.finditer(rf"{word}\s*\(?\s*(\d+)", text):
        lengths.append(int(m.group(1)))
    # de-dup preserving order
    seen, out = set(), []
    for n in lengths:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def parse_strategy(description: str) -> StrategySpec:
    """Best-effort parse of `description` into a :class:`StrategySpec`."""
    text = description.lower()
    spec = StrategySpec(name="Custom Strategy")

    # --- risk phrases --------------------------------------------------------
    spec.stop_loss_pct = _find_pct(text, "stop loss", "stop", "sl", default=2.0) or 2.0
    spec.take_profit_pct = _find_pct(text, "take profit", "target", "tp", default=spec.stop_loss_pct * 2)
    spec.risk_per_trade_pct = _find_pct(text, "risk per trade", "risk", default=1.0) or 1.0
    if "atr" in text and ("stop" in text or "trailing" in text):
        spec.use_atr_stops = True
    spec.allow_short = bool(re.search(r"\bshort\b", text))

    matched = False

    # --- EMA / SMA crossover -------------------------------------------------
    for word, kind in (("ema", "ema"), ("sma", "sma"), ("moving average", "sma")):
        lens = _ma_lengths(text, word)
        if len(lens) >= 2:
            fast, slow = sorted(lens[:2])
            spec.add(Indicator("maFast", kind, length=fast))
            spec.add(Indicator("maSlow", kind, length=slow))
            up = "crossover" if not _wants_under(text) else ">"
            spec.long_entry.append(Rule("maFast", up, "maSlow"))
            spec.long_exit.append(Rule("maFast", "crossunder", "maSlow"))
            if spec.allow_short:
                spec.short_entry.append(Rule("maFast", "crossunder", "maSlow"))
                spec.short_exit.append(Rule("maFast", "crossover", "maSlow"))
            matched = True
            break

    # --- RSI -----------------------------------------------------------------
    if "rsi" in text:
        rsi_lens = _ma_lengths(text, "rsi")
        length = rsi_lens[0] if rsi_lens else 14
        oversold = _find_pct(text, "oversold", default=None)
        overbought = _find_pct(text, "overbought", default=None)
        # also catch bare "below 30" / "above 70"
        below = re.search(r"below\s*(\d+)", text)
        above = re.search(r"above\s*(\d+)", text)
        oversold = oversold or (float(below.group(1)) if below else 30.0)
        overbought = overbought or (float(above.group(1)) if above else 70.0)
        spec.add(Indicator("rsi", "rsi", length=length))
        spec.add(Indicator("rsiOS", "const", value=oversold))
        spec.add(Indicator("rsiOB", "const", value=overbought))
        if matched:
            # use RSI as a momentum confirmation on the trend entry
            spec.long_entry.append(Rule("rsi", "crossover", "rsiOS"))
        else:
            spec.long_entry.append(Rule("rsi", "crossover", "rsiOS"))
            spec.long_exit.append(Rule("rsi", "crossover", "rsiOB"))
            matched = True

    # --- MACD ----------------------------------------------------------------
    if "macd" in text and not matched:
        spec.add(Indicator("macdLine", "macd_line"))
        spec.add(Indicator("macdSig", "macd_signal"))
        spec.long_entry.append(Rule("macdLine", "crossover", "macdSig"))
        spec.long_exit.append(Rule("macdLine", "crossunder", "macdSig"))
        matched = True

    # --- Bollinger -----------------------------------------------------------
    if ("bollinger" in text or "bands" in text) and not matched:
        spec.add(Indicator("price", "close"))
        spec.add(Indicator("bbUpper", "bb_upper", length=20))
        spec.add(Indicator("bbBasis", "bb_basis", length=20))
        spec.long_entry.append(Rule("price", "crossover", "bbUpper"))
        spec.long_exit.append(Rule("price", "crossunder", "bbBasis"))
        matched = True

    if not matched:
        # Sensible default so we always return something runnable.
        spec.add(Indicator("maFast", "ema", length=12))
        spec.add(Indicator("maSlow", "ema", length=26))
        spec.long_entry.append(Rule("maFast", "crossover", "maSlow"))
        spec.long_exit.append(Rule("maFast", "crossunder", "maSlow"))
        spec.name = "Custom Strategy (default EMA crossover)"

    spec.validate()
    return spec


def _wants_under(text: str) -> bool:
    return False  # reserved for future "stay above" vs "cross above" nuance
