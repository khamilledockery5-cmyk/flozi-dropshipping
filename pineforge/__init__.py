"""PineForge — an AI Pine Script generator for TradingView.

Describe a trading strategy in plain English and get back a ready-to-paste
TradingView **Pine Script v6** `strategy()` script, complete with risk
management (hard stop loss, take profit, risk-based position sizing) so you can
backtest it on any chart.

Two ways to turn words into a strategy:

* ``parser``    — a dependency-free keyword parser (works fully offline).
* ``ai``        — a Claude-powered parser (``claude-opus-4-8``) that handles
                  free-form descriptions via structured outputs. Falls back to
                  the offline parser when no API key / SDK is available.

Both produce a validated :class:`StrategySpec`, which the deterministic
:mod:`generator` turns into Pine Script. Generating from a structured spec
(rather than letting an LLM free-write code) keeps the output valid,
reproducible, and auditable.
"""

from __future__ import annotations

__version__ = "1.0.0"

from .spec import Indicator, Rule, StrategySpec
from .generator import generate_pine
from .validator import validate_pine, ValidationResult
from .parser import parse_strategy
from . import library

__all__ = [
    "Indicator",
    "Rule",
    "StrategySpec",
    "generate_pine",
    "validate_pine",
    "ValidationResult",
    "parse_strategy",
    "library",
    "__version__",
]
