import unittest

from trading_bot.config import Config
from trading_bot.strategy import Signal, Strategy


class TestStrategy(unittest.TestCase):
    def test_warmup_is_hold(self):
        cfg = Config()
        states = Strategy(cfg).generate([100.0] * 5)
        self.assertTrue(all(s.signal == Signal.HOLD for s in states))

    def test_signals_have_aligned_length(self):
        cfg = Config()
        closes = [100 + i * 0.1 for i in range(100)]
        states = Strategy(cfg).generate(closes)
        self.assertEqual(len(states), len(closes))

    def test_downtrend_never_buys(self):
        cfg = Config()
        closes = [200 - i for i in range(100)]  # strictly falling
        states = Strategy(cfg).generate(closes)
        self.assertFalse(any(s.signal == Signal.BUY for s in states))

    def test_golden_cross_produces_a_buy(self):
        # gentle recovery after a downtrend: EMA golden-crosses while RSI is
        # still moderate (not yet overbought)
        closes = [200 - i for i in range(60)]                 # downtrend
        closes += [closes[-1] + i * 0.4 for i in range(80)]   # gentle recovery
        states = Strategy(Config()).generate(closes)
        buys = [s for s in states if s.signal == Signal.BUY]
        self.assertTrue(buys, "expected at least one BUY on the recovery")
        self.assertTrue(all("EMA" in b.reason or "pullback" in b.reason for b in buys))

    def test_buys_appear_on_realistic_data(self):
        from trading_bot.data import synthetic_ohlc, closes as bar_closes
        bars = synthetic_ohlc(n=500, seed=42)
        states = Strategy(Config()).generate(bar_closes(bars))
        self.assertTrue(any(s.signal == Signal.BUY for s in states))

    def test_overbought_triggers_sell(self):
        closes = [float(i) for i in range(1, 80)]  # relentless rally -> RSI maxes
        states = Strategy(Config()).generate(closes)
        self.assertTrue(any(s.signal == Signal.SELL for s in states))


if __name__ == "__main__":
    unittest.main()
