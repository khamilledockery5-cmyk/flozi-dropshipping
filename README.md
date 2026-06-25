# Flozi Trading Bot 🤖📈

A **dependency-free** (pure Python 3.9+) algorithmic trading bot with a clear,
auditable strategy and **strict risk management** — every trade is protected by
a hard **2% stop loss** and sized so a single loss only costs ~1% of your
account.

> ⚠️ **Read this first.** No bot can *guarantee* profit. Markets are
> uncertain and most strategies lose money over some periods. What this bot
> *does* guarantee is **disciplined risk control**: it never lets a single
> trade lose more than your configured stop (default 2%). That is how serious
> traders survive — protect the downside, and let winners run. This software is
> for **education and paper trading**. It is **not financial advice**. Do not
> risk money you can't afford to lose.

---

## What "the right strategy, the right way" means here

1. **Trade *with* the trend, not against it.** Entries only happen when the
   trend (fast EMA vs slow EMA) supports the direction.
2. **Confirm with momentum (RSI).** Either catch a fresh trend (golden cross)
   or buy a healthy pullback — never chase an already-overbought move.
3. **Cut losses fast, the 2% rule.** Every position has a hard stop. If it's
   hit, the bot is out. No "hoping it comes back."
4. **Size by risk, not by greed.** Position size is computed so that *being
   wrong* costs a fixed, small fraction of equity (default 1%).
5. **Aim for asymmetry.** Default target is 2× the risk (4% take-profit vs 2%
   stop), so winners can outweigh losers even with a sub-50% win rate.

## Quick start

```bash
# Backtest on built-in offline synthetic data (no network, no install)
python -m trading_bot backtest --bars 750

# Backtest your own OHLC data
python -m trading_bot backtest --csv your_prices.csv --symbol BTCUSD

# Watch a paper-trading session print every BUY/SELL decision
python -m trading_bot paper --bars 400

# Show the active configuration
python -m trading_bot config

# Run the test suite
python -m unittest discover -s tests
```

### Example output

```
=== Backtest on 750 bars ===
Symbol:           DEMO
Starting equity:  $10,000.00
Ending equity:    $9,374.51
Total return:     -6.25%
Max drawdown:     6.25%
Trades:           11
Win rate:         18.2%
Profit factor:    0.39
Worst trade:      -2.05%      <-- the 2% stop loss in action
```

(That negative example on random-walk data is intentional — it shows the bot
being honest. The point isn't that this strategy prints money on noise; it's
that **no trade blew past the 2% stop**. Tune parameters and test on real data
before drawing conclusions.)

## Configuration

All knobs live in [`trading_bot/config.py`](trading_bot/config.py). Key ones:

| Parameter         | Default | Meaning                                            |
|-------------------|---------|----------------------------------------------------|
| `stop_loss_pct`   | `0.02`  | **Hard 2% stop loss per trade** (the core rule)    |
| `take_profit_pct` | `0.04`  | Profit target (2:1 reward:risk)                    |
| `risk_per_trade`  | `0.01`  | Max % of equity risked on any one trade            |
| `fast_ema` / `slow_ema` | 12/26 | Trend filter                                  |
| `rsi_period`      | `14`    | Momentum lookback                                  |
| `fee_pct` / `slippage_pct` | 0.001 / 0.0005 | Modeled trading costs               |
| `allow_short`     | `False` | Long-only by default (safer)                       |
| `use_atr_stops`   | `False` | Widen stops by volatility, keeping $ risk constant |

CLI flags override defaults, e.g. `--stop 2 --target 4 --risk 1`.

## Project layout

```
trading_bot/
├── config.py      # all tunable parameters + validation
├── indicators.py  # EMA / RSI / ATR (pure Python)
├── strategy.py    # trend + momentum -> BUY / SELL / HOLD
├── risk.py        # 2% stop loss + risk-based position sizing
├── backtest.py    # event-driven simulator + performance stats
├── bot.py         # orchestrator: backtest + streaming paper trader
├── data.py        # CSV loader + offline synthetic data generator
└── cli.py         # `python -m trading_bot ...`
tests/             # unit tests for every module (run with unittest)
```

## CSV format

```csv
timestamp,open,high,low,close,volume
2024-01-01,100.0,101.2,99.5,100.8,12345
```

Only `open,high,low,close` are required.

## Going live (important)

This bot trades **on paper only**. There is no broker/exchange connection by
design. To trade real money you would implement order submission against a
broker API inside `bot.py` — but only after you have:

- backtested across **many** market regimes (bull, bear, sideways),
- forward-tested on paper for a meaningful period,
- confirmed the strategy's edge survives realistic fees and slippage, and
- accepted that you can lose money regardless.

Risk management protects you; it doesn't make you money. Trade responsibly.
