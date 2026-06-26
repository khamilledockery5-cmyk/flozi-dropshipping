"""Command-line interface for PineForge.

Examples
--------
    # Generate Pine Script from plain English (offline keyword parser)
    python -m pineforge generate "buy when the 50 EMA crosses above the 200 EMA, 2% stop loss, risk 1%"

    # Use Claude for free-form descriptions (needs ANTHROPIC_API_KEY)
    python -m pineforge generate --ai "fade RSI extremes on BTC but only with the trend, 1.5% stop"

    # Start from a pre-built template
    python -m pineforge template ema_rsi_trend
    python -m pineforge list

    # Save to a file
    python -m pineforge generate "macd crossover with 3% stop" -o strategy.pine
"""

from __future__ import annotations

import argparse
import sys

from . import ai, library
from .generator import generate_pine
from .parser import parse_strategy
from .validator import validate_pine


def _emit(code: str, out: str | None) -> int:
    result = validate_pine(code)
    if out:
        with open(out, "w") as fh:
            fh.write(code)
        print(f"Wrote {len(code.splitlines())} lines to {out}")
    else:
        print(code)
    for w in result.warnings:
        print(f"  warning: {w}", file=sys.stderr)
    if not result.ok:
        for e in result.errors:
            print(f"  error: {e}", file=sys.stderr)
        return 1
    return 0


def cmd_generate(args) -> int:
    if args.ai:
        if not ai.available():
            print("AI mode unavailable (need 'anthropic' + ANTHROPIC_API_KEY); "
                  "falling back to the offline parser.", file=sys.stderr)
            spec = parse_strategy(args.description)
        else:
            spec = ai.generate_spec_with_ai(args.description)
    else:
        spec = parse_strategy(args.description)
    return _emit(generate_pine(spec), args.output)


def cmd_template(args) -> int:
    spec = library.get(args.name)
    return _emit(generate_pine(spec), args.output)


def cmd_list(args) -> int:
    print("Available templates:")
    for name, fn in sorted(library.TEMPLATES.items()):
        spec = fn()
        print(f"  {name:20s} {spec.name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pineforge",
        description="AI Pine Script generator for TradingView — describe a "
                    "strategy, get a backtestable script with risk management.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    g = sub.add_parser("generate", help="generate Pine Script from a description")
    g.add_argument("description", help="plain-English strategy description")
    g.add_argument("--ai", action="store_true", help="use Claude (needs ANTHROPIC_API_KEY)")
    g.add_argument("-o", "--output", help="write to a file instead of stdout")
    g.set_defaults(func=cmd_generate)

    t = sub.add_parser("template", help="generate from a pre-built template")
    t.add_argument("name", help="template name (see `pineforge list`)")
    t.add_argument("-o", "--output", help="write to a file instead of stdout")
    t.set_defaults(func=cmd_template)

    ls = sub.add_parser("list", help="list available templates")
    ls.set_defaults(func=cmd_list)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
