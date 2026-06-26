"""Turn a :class:`StrategySpec` into TradingView Pine Script v6.

The generated script is a backtestable ``strategy()`` with:
  * each indicator declared once (shared MACD/Bollinger computations de-duped),
  * long (and optional short) entry/exit conditions,
  * a hard percentage **stop loss** and **take profit** per trade,
  * risk-based **position sizing** (size so a stop-out costs a fixed % of equity),
  * commission modeled so the backtest isn't fantasy.

The output is plain text you paste into TradingView's Pine editor.
"""

from __future__ import annotations

from typing import List

from .spec import (
    Indicator,
    Rule,
    StrategySpec,
    PRICE_KINDS,
    SINGLE_SOURCE_MA,
    CROSS_OPS,
)


def _emit_indicator(ind: Indicator, shared: dict, lines: List[str]) -> None:
    """Append the Pine declaration(s) for one indicator."""
    k = ind.id
    if ind.kind in PRICE_KINDS:
        lines.append(f"{k} = {ind.kind}")
    elif ind.kind == "const":
        lines.append(f"{k} = {ind.value}")
    elif ind.kind in SINGLE_SOURCE_MA:
        lines.append(f"{k} = ta.{ind.kind}({ind.source}, {ind.length})")
    elif ind.kind == "rsi":
        lines.append(f"{k} = ta.rsi({ind.source}, {ind.length})")
    elif ind.kind == "atr":
        lines.append(f"{k} = ta.atr({ind.length})")
    elif ind.kind == "stdev":
        lines.append(f"{k} = ta.stdev({ind.source}, {ind.length})")
    elif ind.kind in ("macd_line", "macd_signal", "macd_hist"):
        key = ("macd", ind.source, ind.fast, ind.slow, ind.signal)
        prefix = shared.get(key)
        if prefix is None:
            prefix = f"_macd{len(shared)}"
            shared[key] = prefix
            lines.append(
                f"[{prefix}Line, {prefix}Signal, {prefix}Hist] = "
                f"ta.macd({ind.source}, {ind.fast}, {ind.slow}, {ind.signal})"
            )
        suffix = {"macd_line": "Line", "macd_signal": "Signal", "macd_hist": "Hist"}[ind.kind]
        lines.append(f"{k} = {prefix}{suffix}")
    elif ind.kind in ("bb_basis", "bb_upper", "bb_lower"):
        key = ("bb", ind.source, ind.length, ind.mult)
        prefix = shared.get(key)
        if prefix is None:
            prefix = f"_bb{len(shared)}"
            shared[key] = prefix
            lines.append(f"{prefix}Basis = ta.sma({ind.source}, {ind.length})")
            lines.append(f"{prefix}Dev = {ind.mult} * ta.stdev({ind.source}, {ind.length})")
        if ind.kind == "bb_basis":
            lines.append(f"{k} = {prefix}Basis")
        elif ind.kind == "bb_upper":
            lines.append(f"{k} = {prefix}Basis + {prefix}Dev")
        else:
            lines.append(f"{k} = {prefix}Basis - {prefix}Dev")
    else:  # pragma: no cover - guarded by spec validation
        raise ValueError(f"cannot emit indicator kind {ind.kind!r}")


def _emit_rule(rule: Rule) -> str:
    if rule.op in CROSS_OPS:
        return f"ta.{rule.op}({rule.left}, {rule.right})"
    return f"{rule.left} {rule.op} {rule.right}"


def _combine(rules: List[Rule], joiner: str) -> str:
    if not rules:
        return "false"
    return f" {joiner} ".join(f"({_emit_rule(r)})" for r in rules)


def generate_pine(spec: StrategySpec) -> str:
    """Render `spec` as a Pine Script v6 strategy string."""
    spec.validate()
    L: List[str] = []
    overlay = "true" if spec.overlay else "false"

    L.append("//@version=6")
    L.append(
        f'strategy("{spec.name}", overlay={overlay}, '
        f"initial_capital={spec.initial_capital:.0f}, "
        "currency=currency.USD, "
        "commission_type=strategy.commission.percent, "
        f"commission_value={spec.commission_pct}, "
        "calc_on_order_fills=false, process_orders_on_close=true)"
    )
    L.append("")
    L.append("// === Risk inputs (the 2% loss rule lives here) ===")
    L.append(f"stopLossPct   = input.float({spec.stop_loss_pct}, \"Stop loss %\", minval=0.1) / 100.0")
    L.append(f"takeProfitPct = input.float({spec.take_profit_pct}, \"Take profit %\", minval=0.1) / 100.0")
    L.append(f"riskPerTrade  = input.float({spec.risk_per_trade_pct}, \"Risk per trade %\", minval=0.1) / 100.0")
    if spec.use_atr_stops:
        L.append(f"atrStopMult   = input.float({spec.atr_mult}, \"ATR stop multiplier\", minval=0.1)")
    L.append("")

    L.append("// === Indicators ===")
    shared: dict = {}
    for ind in spec.indicators.values():
        _emit_indicator(ind, shared, L)
    if spec.use_atr_stops and not any(i.kind == "atr" for i in spec.indicators.values()):
        L.append(f"_riskAtr = ta.atr({spec.atr_length})")
        atr_var = "_riskAtr"
    elif spec.use_atr_stops:
        atr_var = next(i.id for i in spec.indicators.values() if i.kind == "atr")
    else:
        atr_var = None
    L.append("")

    L.append("// === Signals ===")
    L.append(f"longEntry  = {_combine(spec.long_entry, 'and')}")
    L.append(f"longExit   = {_combine(spec.long_exit, 'or')}")
    if spec.allow_short:
        L.append(f"shortEntry = {_combine(spec.short_entry, 'and')}")
        L.append(f"shortExit  = {_combine(spec.short_exit, 'or')}")
    L.append("")

    L.append("// === Risk-based position sizing ===")
    if spec.use_atr_stops and atr_var:
        L.append(f"stopDist = math.max(close * stopLossPct, {atr_var} * atrStopMult)")
    else:
        L.append("stopDist = close * stopLossPct")
    L.append("// size so that being stopped out loses ~riskPerTrade of equity")
    L.append("riskCapital = strategy.equity * riskPerTrade")
    L.append("qty = stopDist > 0 ? riskCapital / stopDist : 0.0")
    L.append("// never exceed 100% of equity in notional")
    L.append("maxQty = strategy.equity / close")
    L.append("qty := math.min(qty, maxQty)")
    L.append("")

    L.append("// === Orders ===")
    L.append("if longEntry and strategy.position_size == 0 and qty > 0")
    L.append("    strategy.entry(\"Long\", strategy.long, qty=qty)")
    L.append("    longStop = close - stopDist")
    L.append("    longTP   = close * (1 + takeProfitPct)")
    L.append("    strategy.exit(\"Long X\", from_entry=\"Long\", stop=longStop, limit=longTP)")
    L.append("if longExit")
    L.append("    strategy.close(\"Long\")")
    if spec.allow_short:
        L.append("if shortEntry and strategy.position_size == 0 and qty > 0")
        L.append("    strategy.entry(\"Short\", strategy.short, qty=qty)")
        L.append("    shortStop = close + stopDist")
        L.append("    shortTP   = close * (1 - takeProfitPct)")
        L.append("    strategy.exit(\"Short X\", from_entry=\"Short\", stop=shortStop, limit=shortTP)")
        L.append("if shortExit")
        L.append("    strategy.close(\"Short\")")
    L.append("")

    L.append("// === Plots ===")
    for ind in spec.indicators.values():
        if ind.kind in SINGLE_SOURCE_MA or ind.kind.startswith("bb_"):
            L.append(f"plot({ind.id}, \"{ind.id}\")")
    L.append("")
    return "\n".join(L)
