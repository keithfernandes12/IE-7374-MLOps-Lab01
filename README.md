# LAB1 - MLOps (IE-7374): E-commerce Sales Metrics

![Pytest](https://github.com/keithfernandes12/IE-7374-MLOps-Lab01/actions/workflows/pytest_action.yml/badge.svg)
![Unittest](https://github.com/keithfernandes12/IE-7374-MLOps-Lab01/actions/workflows/unittest_action.yml/badge.svg)

This lab covers creating a virtual environment, a GitHub repository, Python source files, tests with pytest and unittest, and GitHub Actions that run those tests on every push.

It is based on the [original Lab 1](https://github.com/raminmohammadi/MLOps/tree/main/Labs/Github_Labs/Lab1). The original tests four calculator functions. This version tests a data-driven module that loads, validates and analyzes an e-commerce orders dataset.

## What's different from the original lab

| | Original lab | This version |
|---|---|---|
| Source code | `calculator.py`: add, subtract, multiply, sum of three | `sales_metrics.py`: load, validate and summarize order data with pandas |
| Data | Empty `data/` folder | `data/orders.csv`: 150 order lines, including 6 deliberately bad rows |
| Error handling tests | None | Missing files, missing columns, invalid inputs, empty data |
| Parametrized tests | Commented out | Used for discounts and top-N products |
| Test fixtures | None | A pytest fixture and a shared, hand-checked sample dataset |
| GitHub Actions | `@v2` actions and Python 3.8, which no longer run | `@v4`/`@v5` actions and Python 3.12; also run on pull requests to `main` |

## Project structure

```
.
├── .github/workflows/
│   ├── pytest_action.yml      # Runs pytest and uploads a JUnit XML report
│   └── unittest_action.yml    # Runs the unittest suite
├── data/
│   └── orders.csv             # Synthetic e-commerce orders
├── src/
│   └── sales_metrics.py       # Functions under test
├── test/
│   ├── sample_data.py         # Small hand-checked dataset shared by both suites
│   ├── test_pytest.py
│   └── test_unittest.py
└── requirements.txt
```

## The dataset

`data/orders.csv` is synthetic, so no real customer data is involved. Each row is one **order line**: one product within an order. An order can have several lines, so `order_id` repeats.

| Column | Example | Description |
|---|---|---|
| `order_id` | `ORD-0003` | Order identifier |
| `order_date` | `2026-04-14` | Date the order was placed |
| `customer_id` | `CUST-027` | Customer identifier |
| `product` | `Cast Iron Skillet` | Product name |
| `category` | `Home & Kitchen` | One of 5 product categories |
| `quantity` | `2` | Units ordered |
| `unit_price` | `34.99` | Price per unit |
| `discount` | `0.1` | Fractional discount (0.1 = 10% off) |

Six rows have deliberate problems (zero or negative quantity, missing or negative price, discount outside 0-1). `validate_orders()` is expected to catch all six.

## Functions in `src/sales_metrics.py`

| Function | What it does |
|---|---|
| `load_orders(path)` | Reads the CSV, checks the required columns are present and parses dates |
| `validate_orders(df)` | Splits rows into `(valid, invalid)` |
| `apply_discount(price, discount)` | Applies a fractional discount and validates both inputs |
| `add_line_total(df)` | Adds `quantity * unit_price * (1 - discount)` as a new column |
| `total_revenue(df)` | Total revenue after discounts |
| `average_order_value(df)` | Revenue per distinct order, not per order line |
| `revenue_by_category(df)` | Revenue per category, highest first |
| `top_products(df, n)` | Top `n` products by units sold |
| `monthly_revenue(df)` | Revenue per calendar month |

## Running locally

1. Create and activate a virtual environment:
    ```
    python -m venv lab_01
    lab_01\Scripts\activate          # Windows
    source lab_01/bin/activate       # macOS / Linux
    ```
2. Install the dependencies:
    ```
    pip install -r requirements.txt
    ```
3. Run the tests from the project root:
    ```
    pytest
    python -m unittest test.test_unittest
    ```

## GitHub Actions

Both workflows run on every push and pull request to `main`. Results are in the repository's **Actions** tab.

- **`pytest_action.yml`** (Testing with Pytest): installs dependencies, runs `pytest --junitxml=pytest-report.xml`, and uploads the report as the `test-results` artifact even if tests fail. It also runs on pushes to `releases/**` branches.
- **`unittest_action.yml`** (Python Unittests): installs dependencies and runs `python -m unittest test.test_unittest`.

Both workflows end with a step that prints whether the tests passed or failed.
