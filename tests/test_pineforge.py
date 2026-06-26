import unittest

from pineforge import (
    Indicator,
    Rule,
    StrategySpec,
    generate_pine,
    validate_pine,
    parse_strategy,
    library,
)
from pineforge import ai


class TestSpec(unittest.TestCase):
    def test_rejects_unknown_kind(self):
        with self.assertRaises(ValueError):
            Indicator("x", "not_a_real_indicator")

    def test_rejects_bad_operator(self):
        with self.assertRaises(ValueError):
            Rule("a", "≈", "b")

    def test_validate_requires_entries(self):
        with self.assertRaises(ValueError):
            StrategySpec().validate()

    def test_validate_catches_dangling_reference(self):
        s = StrategySpec()
        s.add(Indicator("a", "ema", length=10))
        s.long_entry = [Rule("a", ">", "ghost")]
        with self.assertRaises(ValueError):
            s.validate()


class TestGenerator(unittest.TestCase):
    def test_templates_all_generate_valid_pine(self):
        for name in library.TEMPLATES:
            spec = library.get(name)
            code = generate_pine(spec)
            result = validate_pine(code)
            self.assertTrue(result.ok, f"{name}: {result.errors}")
            self.assertIn("//@version=6", code)
            self.assertIn("strategy.entry", code)

    def test_stop_loss_appears_in_output(self):
        code = generate_pine(library.ema_crossover())
        self.assertIn("stopLossPct", code)
        self.assertIn("strategy.exit", code)
        self.assertIn("riskPerTrade", code)  # risk-based sizing present

    def test_macd_computed_once(self):
        # macd_line and macd_signal share one ta.macd() call
        code = generate_pine(library.macd_trend())
        self.assertEqual(code.count("ta.macd("), 1)

    def test_bollinger_shares_basis(self):
        code = generate_pine(library.bollinger_breakout())
        # basis sma computed once even though basis + upper both use it
        self.assertEqual(code.count("ta.sma("), 1)

    def test_short_block_only_when_allowed(self):
        long_only = generate_pine(library.ema_crossover())
        self.assertNotIn("strategy.short", long_only)
        s = library.ema_crossover()
        s.allow_short = True
        s.short_entry = [Rule("emaFast", "crossunder", "emaSlow")]
        s.short_exit = [Rule("emaFast", "crossover", "emaSlow")]
        self.assertIn("strategy.short", generate_pine(s))

    def test_atr_stops_emit_atr(self):
        s = library.ema_crossover()
        s.use_atr_stops = True
        code = generate_pine(s)
        self.assertIn("ta.atr(", code)
        self.assertIn("atrStopMult", code)


class TestValidator(unittest.TestCase):
    def test_unbalanced_brackets_flagged(self):
        self.assertFalse(validate_pine("//@version=6\nstrategy(\nstrategy.entry(").ok)

    def test_missing_version_flagged(self):
        self.assertFalse(validate_pine("strategy('x')\nstrategy.entry()").ok)

    def test_balanced_strings_ok(self):
        good = generate_pine(library.rsi_reversion())
        self.assertTrue(validate_pine(good).ok)


class TestParser(unittest.TestCase):
    def test_ema_crossover_phrase(self):
        spec = parse_strategy("buy when the 50 EMA crosses above the 200 EMA")
        self.assertIn("maFast", spec.indicators)
        self.assertEqual(spec.indicators["maFast"].length, 50)
        self.assertEqual(spec.indicators["maSlow"].length, 200)
        self.assertTrue(spec.long_entry)

    def test_stop_loss_and_risk_extracted(self):
        spec = parse_strategy("ema crossover with a 1.5% stop loss and risk 0.5% per trade")
        self.assertAlmostEqual(spec.stop_loss_pct, 1.5)
        self.assertAlmostEqual(spec.risk_per_trade_pct, 0.5)

    def test_rsi_phrase(self):
        spec = parse_strategy("buy when rsi drops below 25 and sell above 75")
        self.assertIn("rsi", spec.indicators)
        self.assertEqual(spec.indicators["rsiOS"].value, 25.0)
        self.assertEqual(spec.indicators["rsiOB"].value, 75.0)

    def test_macd_phrase(self):
        spec = parse_strategy("go long on a macd crossover")
        self.assertIn("macdLine", spec.indicators)

    def test_bollinger_phrase(self):
        spec = parse_strategy("breakout above the bollinger bands")
        self.assertIn("bbUpper", spec.indicators)

    def test_unrecognized_still_produces_runnable_spec(self):
        spec = parse_strategy("do something clever with the market")
        code = generate_pine(spec)  # must not raise
        self.assertTrue(validate_pine(code).ok)

    def test_every_parse_generates_valid_pine(self):
        phrases = [
            "12/26 ema crossover, 2% stop, 4% target",
            "rsi reversion below 30 above 70",
            "macd trend following with 3% stop loss",
            "bollinger band breakout strategy",
        ]
        for p in phrases:
            self.assertTrue(validate_pine(generate_pine(parse_strategy(p))).ok, p)


class TestAILayer(unittest.TestCase):
    """The AI layer needs a network/key; test only the offline pieces."""

    def test_spec_from_dict_roundtrip(self):
        data = {
            "name": "Test",
            "indicators": [
                {"id": "emaFast", "kind": "ema", "length": 9},
                {"id": "emaSlow", "kind": "ema", "length": 21},
            ],
            "long_entry": [{"left": "emaFast", "op": "crossover", "right": "emaSlow"}],
            "long_exit": [{"left": "emaFast", "op": "crossunder", "right": "emaSlow"}],
            "stop_loss_pct": 2.5,
        }
        spec = ai.spec_from_dict(data)
        self.assertEqual(spec.stop_loss_pct, 2.5)
        self.assertTrue(validate_pine(generate_pine(spec)).ok)

    def test_schema_enum_matches_supported_kinds(self):
        kinds = ai.SPEC_SCHEMA["properties"]["indicators"]["items"]["properties"]["kind"]["enum"]
        self.assertIn("ema", kinds)
        self.assertIn("macd_line", kinds)


if __name__ == "__main__":
    unittest.main()
