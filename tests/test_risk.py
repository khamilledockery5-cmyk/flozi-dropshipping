import unittest

from trading_bot.config import Config
from trading_bot.risk import build_bracket, stop_distance, stop_hit, take_profit_hit


class TestRisk(unittest.TestCase):
    def setUp(self):
        self.cfg = Config(stop_loss_pct=0.02, risk_per_trade=0.01,
                          take_profit_pct=0.04, max_position_pct=1.0)

    def test_stop_is_two_percent_below_entry(self):
        b = build_bracket(self.cfg, equity=10_000, entry=100.0)
        self.assertAlmostEqual(b.stop, 98.0)            # 2% stop
        self.assertAlmostEqual(b.take_profit, 104.0)    # 4% target

    def test_risk_amount_capped_at_risk_per_trade(self):
        eq = 10_000
        b = build_bracket(self.cfg, equity=eq, entry=100.0)
        # loss if stopped out must be ~1% of equity
        self.assertAlmostEqual(b.risk_amount, eq * 0.01, places=2)
        self.assertLessEqual(b.risk_pct_of_equity, 0.0101)

    def test_position_capped_by_max_position(self):
        cfg = Config(stop_loss_pct=0.02, risk_per_trade=0.5, max_position_pct=1.0)
        # huge risk budget should still not exceed 100% of equity in notional
        b = build_bracket(cfg, equity=10_000, entry=100.0)
        notional = b.quantity * 100.0
        self.assertLessEqual(notional, 10_000 + 1e-6)

    def test_atr_widens_stop(self):
        cfg = Config(use_atr_stops=True, atr_stop_mult=2.0, stop_loss_pct=0.02)
        narrow = stop_distance(Config(), 100.0, atr_value=5.0)
        wide = stop_distance(cfg, 100.0, atr_value=5.0)
        self.assertGreater(wide, narrow)
        self.assertAlmostEqual(wide, 10.0)  # 2 * ATR(5)

    def test_stop_and_target_hits(self):
        b = build_bracket(self.cfg, equity=10_000, entry=100.0)
        self.assertTrue(stop_hit(b, low=97.0, high=99.0))
        self.assertFalse(stop_hit(b, low=98.5, high=99.0))
        self.assertTrue(take_profit_hit(b, low=103, high=105))

    def test_invalid_entry_raises(self):
        with self.assertRaises(ValueError):
            build_bracket(self.cfg, equity=10_000, entry=0.0)


if __name__ == "__main__":
    unittest.main()
