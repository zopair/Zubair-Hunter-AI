import math
import unittest

from trading_lab_v2.data_quality import validate_rows
from trading_lab_v2.objective import TradeResult, expectancy, profit_factor, max_drawdown, score


class DataQualityTests(unittest.TestCase):
    def test_valid_rows_pass(self):
        report = validate_rows([
            {"timestamp": 1, "price": 100, "quantity": 0.5, "is_buyer_maker": True},
            {"timestamp": 2, "price": 101, "quantity": 0.4, "is_buyer_maker": False},
        ])
        self.assertTrue(report.ok)
        self.assertEqual(report.rows, 2)

    def test_empty_dataset_fails(self):
        self.assertFalse(validate_rows([]).ok)

    def test_malformed_and_non_finite_values_are_quarantined(self):
        report = validate_rows([
            {"timestamp": "bad", "price": "not-a-number", "quantity": None},
            {"timestamp": float("nan"), "price": float("inf"), "quantity": -1},
            {"timestamp": True, "price": 0, "quantity": float("nan")},
        ])
        self.assertEqual(report.bad_timestamps, 3)
        self.assertEqual(report.bad_prices, 3)
        self.assertEqual(report.bad_quantities, 3)
        self.assertFalse(report.ok)

    def test_non_boolean_trade_side_is_suspicious(self):
        report = validate_rows([{"timestamp": 1, "price": 1, "quantity": 1, "is_buyer_maker": "false"}])
        self.assertTrue(report.suspicious_side_ratio)
        self.assertFalse(report.ok)

    def test_extreme_one_sided_trade_side_is_suspicious(self):
        rows = [{"timestamp": i, "price": 1, "quantity": 1, "is_buyer_maker": True} for i in range(100)]
        self.assertTrue(validate_rows(rows).suspicious_side_ratio)


class ObjectiveTests(unittest.TestCase):
    def test_net_expectancy_includes_all_execution_costs(self):
        trades = [TradeResult(10, 1, 0.5, 0.5, 2, 4), TradeResult(-2, 0.2, 0.1, 0.1, 3, 0)]
        self.assertAlmostEqual(expectancy(trades), 2.8)

    def test_profit_factor_and_drawdown(self):
        trades = [TradeResult(5, 0, 0, 0, 0, 5), TradeResult(-2, 0, 0, 0, 2, 0)]
        self.assertAlmostEqual(profit_factor(trades), 2.5)
        self.assertAlmostEqual(max_drawdown([100, 120, 90, 110]), 0.25)

    def test_empty_and_no_loss_metrics_are_defined(self):
        self.assertEqual(expectancy([]), 0.0)
        self.assertEqual(profit_factor([]), 0.0)
        self.assertTrue(math.isinf(profit_factor([TradeResult(1, 0, 0, 0, 0, 1)])))


if __name__ == "__main__":
    unittest.main()
