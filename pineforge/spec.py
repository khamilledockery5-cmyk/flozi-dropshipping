"""The strategy specification — the structured intermediate representation.

Natural language (or a template) is turned into a :class:`StrategySpec`, and the
generator turns a :class:`StrategySpec` into Pine Script. Keeping a typed IR in
the middle means the generated code is always syntactically valid and the same
spec always produces the same script.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List

# Indicator kinds the generator knows how to emit.
PRICE_KINDS = {"close", "open", "high", "low", "hl2", "hlc3", "ohlc4"}
SINGLE_SOURCE_MA = {"ema", "sma", "rma", "wma", "vwma"}
COMPUTED_KINDS = {"rsi", "atr", "stdev", "macd_line", "macd_signal", "macd_hist",
                  "bb_upper", "bb_lower", "bb_basis"}
ALL_KINDS = PRICE_KINDS | SINGLE_SOURCE_MA | COMPUTED_KINDS | {"const"}

CROSS_OPS = {"crossover", "crossunder"}
COMPARE_OPS = {">", "<", ">=", "<=", "==", "!="}
ALL_OPS = CROSS_OPS | COMPARE_OPS


@dataclass
class Indicator:
    """A single named value available to the rules.

    ``id`` becomes the Pine variable name. Composite indicators (MACD, Bollinger
    Bands) are represented as several ``Indicator`` entries that share the same
    parameters; the generator de-duplicates the underlying computation.
    """

    id: str
    kind: str
    length: int = 14
    source: str = "close"
    value: float = 0.0          # for kind == "const"
    # MACD params (shared across macd_line / macd_signal / macd_hist)
    fast: int = 12
    slow: int = 26
    signal: int = 9
    # Bollinger params (shared across bb_upper / bb_lower / bb_basis)
    mult: float = 2.0

    def __post_init__(self) -> None:
        if self.kind not in ALL_KINDS:
            raise ValueError(f"unknown indicator kind: {self.kind!r}")
        if not self.id.isidentifier():
            raise ValueError(f"indicator id must be a valid identifier: {self.id!r}")


@dataclass
class Rule:
    """A boolean term: ``<left> <op> <right>`` where both sides are indicator ids."""

    left: str
    op: str
    right: str

    def __post_init__(self) -> None:
        if self.op not in ALL_OPS:
            raise ValueError(f"unknown operator: {self.op!r}")


@dataclass
class StrategySpec:
    name: str = "PineForge Strategy"
    indicators: Dict[str, Indicator] = field(default_factory=dict)
    long_entry: List[Rule] = field(default_factory=list)   # AND-combined
    long_exit: List[Rule] = field(default_factory=list)    # OR-combined
    short_entry: List[Rule] = field(default_factory=list)
    short_exit: List[Rule] = field(default_factory=list)

    # Risk management
    stop_loss_pct: float = 2.0          # the "2% loss" rule, percent of entry
    take_profit_pct: float = 4.0        # percent of entry (default 2:1)
    risk_per_trade_pct: float = 1.0     # percent of equity risked per trade
    use_atr_stops: bool = False
    atr_length: int = 14
    atr_mult: float = 2.0

    # Account
    initial_capital: float = 10_000.0
    commission_pct: float = 0.05        # percent per trade
    allow_short: bool = False
    overlay: bool = True

    def add(self, indicator: Indicator) -> "StrategySpec":
        self.indicators[indicator.id] = indicator
        return self

    def validate(self) -> None:
        if not self.long_entry and not self.short_entry:
            raise ValueError("strategy has no entry conditions")
        if not (0 < self.stop_loss_pct < 100):
            raise ValueError("stop_loss_pct must be between 0 and 100")
        if not (0 < self.risk_per_trade_pct <= 100):
            raise ValueError("risk_per_trade_pct must be between 0 and 100")
        # every rule must reference defined indicators
        refs = set()
        for bucket in (self.long_entry, self.long_exit, self.short_entry, self.short_exit):
            for rule in bucket:
                refs.add(rule.left)
                refs.add(rule.right)
        missing = refs - set(self.indicators)
        if missing:
            raise ValueError(f"rules reference undefined indicators: {sorted(missing)}")
        if self.short_entry and not self.allow_short:
            raise ValueError("short_entry rules present but allow_short is False")

    def to_dict(self) -> dict:
        d = asdict(self)
        # asdict turns nested dataclasses into dicts already
        return d
