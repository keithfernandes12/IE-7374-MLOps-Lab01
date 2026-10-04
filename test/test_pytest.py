from pathlib import Path

import pandas as pd
import pytest

from src import sales_metrics
from .sample_data import make_orders_with_bad_rows, make_sample_orders

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "orders.csv"


@pytest.fixture
def orders():
    return make_sample_orders()


# ---------- load_orders ----------

def test_load_orders_reads_real_dataset():
    df = sales_metrics.load_orders(DATA_PATH)
    assert list(df.columns) == sales_metrics.REQUIRED_COLUMNS
    assert len(df) > 0
    assert pd.api.types.is_datetime64_any_dtype(df["order_date"])


def test_load_orders_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        sales_metrics.load_orders(tmp_path / "does_not_exist.csv")


def test_load_orders_missing_columns_raises(tmp_path):
    csv_path = tmp_path / "orders.csv"
    csv_path.write_text("order_id,quantity\nORD-1,2\n")
    with pytest.raises(ValueError, match="Missing required columns"):
        sales_metrics.load_orders(csv_path)


# ---------- validate_orders ----------

def test_validate_orders_flags_each_bad_row():
    valid, invalid = sales_metrics.validate_orders(make_orders_with_bad_rows())
    assert len(valid) == 4
    assert sorted(invalid["order_id"]) == ["BAD-1", "BAD-2", "BAD-3", "BAD-4"]


def test_validate_orders_keeps_clean_data_unchanged(orders):
    valid, invalid = sales_metrics.validate_orders(orders)
    assert invalid.empty
    pd.testing.assert_frame_equal(valid, orders)


def test_real_dataset_has_six_bad_rows():
    df = sales_metrics.load_orders(DATA_PATH)
    valid, invalid = sales_metrics.validate_orders(df)
    assert len(invalid) == 6
    assert len(valid) + len(invalid) == len(df)


# ---------- apply_discount ----------

@pytest.mark.parametrize("price, discount, expected", [
    (100, 0, 100.00),
    (100, 0.25, 75.00),
    (59.99, 0.10, 53.99),
    (19.99, 1, 0.00),
    (0, 0.5, 0.00),
])
def test_apply_discount(price, discount, expected):
    assert sales_metrics.apply_discount(price, discount) == expected


@pytest.mark.parametrize("price, discount", [
    (-10, 0.1),      # negative price
    (100, -0.1),     # negative discount
    (100, 1.5),      # discount over 100%
    ("100", 0.1),    # price not a number
    (100, None),     # discount not a number
])
def test_apply_discount_invalid_inputs_raise(price, discount):
    with pytest.raises(ValueError):
        sales_metrics.apply_discount(price, discount)


# ---------- revenue metrics ----------

def test_add_line_total(orders):
    result = sales_metrics.add_line_total(orders)
    assert list(result["line_total"]) == [100.00, 18.00, 30.00, 40.00]
    assert "line_total" not in orders.columns  # input is not modified


def test_total_revenue(orders):
    assert sales_metrics.total_revenue(orders) == pytest.approx(188.00)


def test_total_revenue_empty_is_zero(orders):
    assert sales_metrics.total_revenue(orders.iloc[0:0]) == 0.0


def test_average_order_value(orders):
    # 188.00 across 3 distinct orders, not 4 order lines
    assert sales_metrics.average_order_value(orders) == pytest.approx(62.67)


def test_average_order_value_empty_raises(orders):
    with pytest.raises(ValueError, match="No orders"):
        sales_metrics.average_order_value(orders.iloc[0:0])


def test_revenue_by_category(orders):
    result = sales_metrics.revenue_by_category(orders)
    assert list(result.index) == ["Electronics", "Sports", "Books"]
    assert list(result) == [140.00, 30.00, 18.00]


def test_monthly_revenue(orders):
    result = sales_metrics.monthly_revenue(orders)
    assert result.to_dict() == {"2026-01": 148.00, "2026-02": 40.00}


# ---------- top_products ----------

@pytest.mark.parametrize("n, expected", [
    (1, ["Yoga Mat"]),
    (2, ["Yoga Mat", "Wireless Earbuds"]),
    (10, ["Yoga Mat", "Wireless Earbuds", "Atomic Habits"]),  # n larger than product count
])
def test_top_products(orders, n, expected):
    assert list(sales_metrics.top_products(orders, n).index) == expected


def test_top_products_invalid_n_raises(orders):
    with pytest.raises(ValueError):
        sales_metrics.top_products(orders, 0)
