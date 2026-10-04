"""
Small hand-checked orders dataset shared by the pytest and unittest suites.

Line totals (quantity * unit_price * (1 - discount)):
    ORD-1  Wireless Earbuds  2 x 50.00, no discount   = 100.00
    ORD-1  Atomic Habits     1 x 20.00, 10% off       =  18.00
    ORD-2  Yoga Mat          4 x  7.50, no discount   =  30.00
    ORD-3  Wireless Earbuds  1 x 50.00, 20% off       =  40.00

Total revenue = 188.00 across 3 orders, so average order value = 62.67.
"""
import pandas as pd


def make_sample_orders():
    return pd.DataFrame({
        "order_id": ["ORD-1", "ORD-1", "ORD-2", "ORD-3"],
        "order_date": pd.to_datetime(["2026-01-05", "2026-01-05", "2026-01-20", "2026-02-02"]),
        "customer_id": ["CUST-1", "CUST-1", "CUST-2", "CUST-1"],
        "product": ["Wireless Earbuds", "Atomic Habits", "Yoga Mat", "Wireless Earbuds"],
        "category": ["Electronics", "Books", "Sports", "Electronics"],
        "quantity": [2, 1, 4, 1],
        "unit_price": [50.00, 20.00, 7.50, 50.00],
        "discount": [0.0, 0.10, 0.0, 0.20],
    })


def make_orders_with_bad_rows():
    """Sample orders plus one row for each kind of data-quality problem."""
    bad_rows = pd.DataFrame({
        "order_id": ["BAD-1", "BAD-2", "BAD-3", "BAD-4"],
        "order_date": pd.to_datetime(["2026-03-01"] * 4),
        "customer_id": ["CUST-9"] * 4,
        "product": ["Yoga Mat"] * 4,
        "category": ["Sports"] * 4,
        "quantity": [0, 1, 1, 1],                   # BAD-1: zero quantity
        "unit_price": [7.50, None, -7.50, 7.50],    # BAD-2: missing, BAD-3: negative
        "discount": [0.0, 0.0, 0.0, 1.5],           # BAD-4: over 100%
    })
    return pd.concat([make_sample_orders(), bad_rows], ignore_index=True)
