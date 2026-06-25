"""Command-line interface.

Examples
--------
    # Backtest on offline synthetic data (no network needed)
    python -m trading_bot backtest --bars 750

    # Backtest your own data
    python -m trading_bot backtest --csv prices.csv

    # Stream a paper-trading session and print each action
    python -m trading_bot paper --bars 300 --tighten

    # Print the active configuration
    python -m trading_bot config
"""

from __future__ import annotations

import argparse
import sys

from .bot import TradingBot
from .config import Config
from .data import load_csv, synthetic_ohlc


def _build_config(args) -> Config:
    cfg = Config(
        symbol=args.symbol,
        starting_cash=args.cash,
        stop_loss_pct=args.stop / 100.0,
        take_profit_pct=args.target / 100.0,
        risk_per_trade=args.risk / 100.0,
        allow_short=args.allow_short,
        use_atr_stops=args.atr_stops,
    )
    return cfg


def _load_bars(args):
    if args.csv:
        return load_csv(args.csv)
    return synthetic_ohlc(n=args.bars, seed=args.seed)


def cmd_backtest(args) -> int:
    cfg = _build_config(args)
    bars = _load_bars(args)
    result = TradingBot(cfg).backtest(bars)
    print(f"=== Backtest on {len(bars)} bars ===")
    print(result.summary())
    print("\nRisk rule: hard stop loss at "
          f"{cfg.stop_loss_pct*100:.0f}% per trade; "
          f"{cfg.risk_per_trade*100:.2f}% of equity risked per trade.")
    if result.closed_trades:
        worst = result.worst_trade_pct
        print(f"Largest single-trade loss observed: {worst:+.2f}% "
              f"(stop caps intended loss near -{cfg.stop_loss_pct*100:.0f}%).")
    return 0


def cmd_paper(args) -> int:
    cfg = _build_config(args)
    bars = _load_bars(args)
    bot = TradingBot(cfg)
    print(f"=== Paper trading {cfg.symbol} over {len(bars)} bars ===")
    n_actions = 0
    for bar in bars:
        action = bot.on_bar(bar)
        if action:
            n_actions += 1
            print(f"[{bar.timestamp}] {action}")
    final_eq = bot.equity(bars[-1].close)
    ret = (final_eq / cfg.starting_cash - 1.0) * 100.0
    print(f"\nActions: {n_actions} | Final equity: ${final_eq:,.2f} ({ret:+.2f}%)")
    return 0


def cmd_config(args) -> int:
    cfg = _build_config(args)
    for k, v in cfg.to_dict().items():
        print(f"{k:>18}: {v}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="trading_bot",
        description="Dependency-free trend+momentum trading bot with a hard 2% stop loss.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp):
        sp.add_argument("--symbol", default="DEMO")
        sp.add_argument("--csv", help="OHLC CSV file (else synthetic data)")
        sp.add_argument("--bars", type=int, default=500, help="synthetic bar count")
        sp.add_argument("--seed", type=int, default=42, help="synthetic RNG seed")
        sp.add_argument("--cash", type=float, default=10_000.0)
        sp.add_argument("--stop", type=float, default=2.0, help="stop loss %% (default 2)")
        sp.add_argument("--target", type=float, default=4.0, help="take profit %%")
        sp.add_argument("--risk", type=float, default=1.0, help="%% equity risked/trade")
        sp.add_argument("--allow-short", action="store_true")
        sp.add_argument("--atr-stops", action="store_true",
                        help="widen stops by ATR volatility")

    sp = sub.add_parser("backtest", help="run a historical simulation")
    common(sp); sp.set_defaults(func=cmd_backtest)
    sp = sub.add_parser("paper", help="stream a paper-trading session")
    common(sp); sp.set_defaults(func=cmd_paper)
    sp = sub.add_parser("config", help="print the active configuration")
    common(sp); sp.set_defaults(func=cmd_config)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
