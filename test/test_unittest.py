import sys
import os
import unittest

# Get the path to the project's root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from src import sales_metrics
from test.sample_data import make_orders_with_bad_rows, make_sample_orders

DATA_PATH = os.path.join(project_root, "data", "orders.csv")


class TestLoadAndValidate(unittest.TestCase):

    def test_load_orders_reads_real_dataset(self):
        df = sales_metrics.load_orders(DATA_PATH)
        self.assertEqual(list(df.columns), sales_metrics.REQUIRED_COLUMNS)
        self.assertGreater(len(df), 0)

    def test_load_orders_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            sales_metrics.load_orders(os.path.join(project_root, "data", "missing.csv"))

    def test_validate_orders_flags_each_bad_row(self):
        valid, invalid = sales_metrics.validate_orders(make_orders_with_bad_rows())
        self.assertEqual(len(valid), 4)
        self.assertCountEqual(invalid["order_id"], ["BAD-1", "BAD-2", "BAD-3", "BAD-4"])

    def test_real_dataset_has_six_bad_rows(self):
        df = sales_metrics.load_orders(DATA_PATH)
        _, invalid = sales_metrics.validate_orders(df)
        self.assertEqual(len(invalid), 6)


class TestApplyDiscount(unittest.TestCase):

    def test_valid_discounts(self):
        cases = [(100, 0, 100.00), (100, 0.25, 75.00), (59.99, 0.10, 53.99), (19.99, 1, 0.00)]
        for price, discount, expected in cases:
            with self.subTest(price=price, discount=discount):
                self.assertAlmostEqual(sales_metrics.apply_discount(price, discount), expected)

    def test_invalid_inputs_raise(self):
        cases = [(-10, 0.1), (100, -0.1), (100, 1.5), ("100", 0.1), (100, None)]
        for price, discount in cases:
            with self.subTest(price=price, discount=discount):
                with self.assertRaises(ValueError):
                    sales_metrics.apply_discount(price, discount)


class TestRevenueMetrics(unittest.TestCase):

    def setUp(self):
        self.orders = make_sample_orders()

    def test_total_revenue(self):
        self.assertAlmostEqual(sales_metrics.total_revenue(self.orders), 188.00)

    def test_average_order_value(self):
        self.assertAlmostEqual(sales_metrics.average_order_value(self.orders), 62.67)

    def test_average_order_value_empty_raises(self):
        with self.assertRaises(ValueError):
            sales_metrics.average_order_value(self.orders.iloc[0:0])

    def test_revenue_by_category(self):
        result = sales_metrics.revenue_by_category(self.orders)
        self.assertEqual(list(result.index), ["Electronics", "Sports", "Books"])
        self.assertEqual(list(result), [140.00, 30.00, 18.00])

    def test_monthly_revenue(self):
        result = sales_metrics.monthly_revenue(self.orders)
        self.assertEqual(result.to_dict(), {"2026-01": 148.00, "2026-02": 40.00})

    def test_top_products(self):
        result = sales_metrics.top_products(self.orders, 2)
        self.assertEqual(list(result.index), ["Yoga Mat", "Wireless Earbuds"])
        self.assertEqual(list(result), [4, 3])


if __name__ == '__main__':
    unittest.main()
