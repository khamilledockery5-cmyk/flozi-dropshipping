import unittest

from trading_bot.config import Config
from trading_bot.backtest import Backtester
from trading_bot.data import synthetic_ohlc, Bar


class TestBacktest(unittest.TestCase):
    def test_runs_and_produces_curve(self):
        cfg = Config()
        bars = synthetic_ohlc(n=400, seed=1)
        result = Backtester(cfg).run(bars)
        self.assertEqual(len(result.equity_curve), len(bars))
        self.assertGreaterEqual(result.num_trades, 0)
        # summary should render without error
        self.assertIn("Total return", result.summary())

    def test_stop_loss_caps_per_trade_loss(self):
        # With a 2% stop + costs, no single trade should lose dramatically more
        # than the stop distance plus fees/slippage/gap allowance.
        cfg = Config(stop_loss_pct=0.02)
        bars = synthetic_ohlc(n=800, seed=7)
        result = Backtester(cfg).run(bars)
        for t in result.closed_trades:
            # allow generous headroom for gap-throughs + costs, but it must be
            # bounded well above a catastrophic loss
            self.assertGreater(t.return_pct, -25.0)

    def test_no_trades_when_flat_market(self):
        # perfectly flat market -> no momentum setups -> no trades
        bars = [Bar(f"T{i}", 100, 100, 100, 100, 0) for i in range(200)]
        result = Backtester(Config()).run(bars)
        self.assertEqual(result.num_trades, 0)
        self.assertAlmostEqual(result.ending_equity, Config().starting_cash)

    def test_equity_never_nan(self):
        bars = synthetic_ohlc(n=300, seed=3)
        result = Backtester(Config()).run(bars)
        for v in result.equity_curve:
            self.assertEqual(v, v)  # NaN != NaN
            self.assertGreater(v, 0)


if __name__ == "__main__":
    unittest.main()
