"""Claude-powered natural-language → :class:`StrategySpec` layer.

This is the "AI" in the AI Pine Script generator. It asks Claude
(``claude-opus-4-8``) to translate a free-form strategy description into the
structured :class:`StrategySpec` JSON, using **structured outputs** so the
result always conforms to our schema. We then feed that spec through the same
deterministic, validated generator the offline path uses — so even the AI path
produces guaranteed-valid Pine Script.

Design choice: Claude fills in a *structured spec*, not raw Pine code. That
keeps the generated script valid and auditable, and means a model that's a
little off still can't emit code that won't compile.

Requires the ``anthropic`` package and an ``ANTHROPIC_API_KEY`` in the
environment. When neither is available, :func:`generate_spec_with_ai` raises
:class:`AIUnavailable` and callers should fall back to
:func:`pineforge.parser.parse_strategy`.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict

from .spec import Indicator, Rule, StrategySpec, ALL_KINDS, ALL_OPS

MODEL = "claude-opus-4-8"

SYSTEM_PROMPT = """You are a quantitative trading engineer that converts a \
plain-English trading strategy description into a STRUCTURED specification for a \
TradingView Pine Script strategy.

Rules:
- Use ONLY these indicator kinds: ema, sma, rma, wma, vwma, rsi, atr, stdev, \
macd_line, macd_signal, macd_hist, bb_upper, bb_lower, bb_basis, close, open, \
high, low, hl2, hlc3, ohlc4, const.
- Represent numeric thresholds (e.g. RSI 30) as a `const` indicator with `value` set.
- Every rule's `left` and `right` must be the `id` of an indicator you defined.
- Operators: crossover, crossunder, >, <, >=, <=, ==, !=.
- Entry rules are AND-combined; exit rules are OR-combined.
- Always include sensible risk management. If the user gives a stop loss / take \
profit / risk %, use it; otherwise default to a 2% stop, 4% take profit, 1% risk.
- Only set allow_short true and add short rules if the user clearly wants shorting.
- Keep it simple and tradeable; do not invent indicators outside the list."""

# JSON schema for structured outputs (subset the API supports: no min/max etc.)
SPEC_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "name": {"type": "string"},
        "indicators": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "id": {"type": "string"},
                    "kind": {"type": "string", "enum": sorted(ALL_KINDS)},
                    "length": {"type": "integer"},
                    "source": {"type": "string"},
                    "value": {"type": "number"},
                    "fast": {"type": "integer"},
                    "slow": {"type": "integer"},
                    "signal": {"type": "integer"},
                    "mult": {"type": "number"},
                },
                "required": ["id", "kind"],
            },
        },
        "long_entry": {"type": "array", "items": {"$ref": "#/$defs/rule"}},
        "long_exit": {"type": "array", "items": {"$ref": "#/$defs/rule"}},
        "short_entry": {"type": "array", "items": {"$ref": "#/$defs/rule"}},
        "short_exit": {"type": "array", "items": {"$ref": "#/$defs/rule"}},
        "stop_loss_pct": {"type": "number"},
        "take_profit_pct": {"type": "number"},
        "risk_per_trade_pct": {"type": "number"},
        "use_atr_stops": {"type": "boolean"},
        "allow_short": {"type": "boolean"},
    },
    "required": ["name", "indicators", "long_entry"],
    "$defs": {
        "rule": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "left": {"type": "string"},
                "op": {"type": "string", "enum": sorted(ALL_OPS)},
                "right": {"type": "string"},
            },
            "required": ["left", "op", "right"],
        }
    },
}


class AIUnavailable(RuntimeError):
    """Raised when the Anthropic SDK or API key is not available."""


def available() -> bool:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return True


def spec_from_dict(data: Dict[str, Any]) -> StrategySpec:
    """Build a validated :class:`StrategySpec` from the JSON the model returns."""
    spec = StrategySpec(name=data.get("name", "AI Strategy"))
    for raw in data.get("indicators", []):
        spec.add(Indicator(**{k: v for k, v in raw.items() if k in Indicator.__annotations__}))
    for bucket in ("long_entry", "long_exit", "short_entry", "short_exit"):
        rules = [Rule(r["left"], r["op"], r["right"]) for r in data.get(bucket, [])]
        setattr(spec, bucket, rules)
    for f in ("stop_loss_pct", "take_profit_pct", "risk_per_trade_pct",
              "use_atr_stops", "allow_short"):
        if f in data:
            setattr(spec, f, data[f])
    spec.validate()
    return spec


def generate_spec_with_ai(description: str, model: str = MODEL) -> StrategySpec:
    """Use Claude to turn `description` into a :class:`StrategySpec`."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise AIUnavailable("ANTHROPIC_API_KEY is not set")
    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise AIUnavailable("the 'anthropic' package is not installed") from exc

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        output_config={"format": {"type": "json_schema", "schema": SPEC_SCHEMA}},
        messages=[{"role": "user", "content": description}],
    )
    # structured outputs guarantee the first text block is schema-valid JSON
    text = next(b.text for b in response.content if b.type == "text")
    return spec_from_dict(json.loads(text))
