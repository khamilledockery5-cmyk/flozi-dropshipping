import math
import unittest

from trading_bot.indicators import sma, ema, rsi, atr


class TestIndicators(unittest.TestCase):
    def test_sma_basic(self):
        out = sma([1, 2, 3, 4, 5], 3)
        self.assertIsNone(out[0])
        self.assertIsNone(out[1])
        self.assertAlmostEqual(out[2], 2.0)
        self.assertAlmostEqual(out[3], 3.0)
        self.assertAlmostEqual(out[4], 4.0)

    def test_ema_length_and_warmup(self):
        vals = [float(i) for i in range(1, 21)]
        out = ema(vals, 5)
        self.assertEqual(len(out), len(vals))
        self.assertTrue(all(o is None for o in out[:4]))
        self.assertIsNotNone(out[4])

    def test_ema_trends_with_seed(self):
        vals = [10.0] * 10
        out = ema(vals, 5)
        # flat input -> ema equals the constant once warmed up
        self.assertAlmostEqual(out[-1], 10.0)

    def test_rsi_all_gains_is_100(self):
        vals = [float(i) for i in range(1, 30)]
        out = rsi(vals, 14)
        self.assertAlmostEqual(out[-1], 100.0)

    def test_rsi_all_losses_is_low(self):
        vals = [float(i) for i in range(30, 1, -1)]
        out = rsi(vals, 14)
        self.assertLess(out[-1], 1.0)

    def test_rsi_bounds(self):
        import random
        rng = random.Random(0)
        vals = [100.0]
        for _ in range(200):
            vals.append(max(1.0, vals[-1] * (1 + rng.gauss(0, 0.02))))
        out = rsi(vals, 14)
        for v in out:
            if v is not None:
                self.assertGreaterEqual(v, 0.0)
                self.assertLessEqual(v, 100.0)

    def test_atr_positive(self):
        highs = [10, 11, 12, 13, 14, 15]
        lows = [9, 9.5, 10, 11, 12, 13]
        closes = [9.5, 10.5, 11.5, 12.5, 13.5, 14.5]
        out = atr(highs, lows, closes, 3)
        self.assertEqual(len(out), len(closes))
        self.assertTrue(all(v is None or v > 0 for v in out))


if __name__ == "__main__":
    unittest.main()
