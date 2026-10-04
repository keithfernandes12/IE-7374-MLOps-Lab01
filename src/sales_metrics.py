"""
Sales metrics for the e-commerce orders dataset (data/orders.csv).

Each row in the dataset is one order line: a single product within an order.
An order can have several lines, so order_id repeats across rows.
"""
from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = ["order_id", "order_date", "customer_id", "product", "category",
                    "quantity", "unit_price", "discount"]


def load_orders(path):
    """
    Loads the orders CSV and parses order dates.
    Args:
        path (str/Path): Path to the orders CSV file.
    Returns:
        pd.DataFrame: One row per order line.
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If any required column is missing.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Orders file not found: {path}")

    df = pd.read_csv(path)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


def validate_orders(df):
    """
    Splits order lines into valid and invalid rows.
    A row is invalid if quantity, unit_price or discount is missing, quantity is
    zero or negative, unit_price is negative, or discount is outside 0-1.
    Args:
        df (pd.DataFrame): Order lines.
    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: (valid rows, invalid rows).
    """
    is_invalid = (
        df[["quantity", "unit_price", "discount"]].isna().any(axis=1)
        | (df["quantity"] <= 0)
        | (df["unit_price"] < 0)
        | ~df["discount"].between(0, 1)
    )
    return df[~is_invalid].copy(), df[is_invalid].copy()


def apply_discount(price, discount):
    """
    Applies a fractional discount to a price.
    Args:
        price (int/float): Original price.
        discount (int/float): Discount as a fraction, e.g. 0.15 for 15% off.
    Returns:
        float: Discounted price, rounded to 2 decimal places.
    Raises:
        ValueError: If either input is not a number, price is negative,
            or discount is outside 0-1.
    """
    if not (isinstance(price, (int, float)) and isinstance(discount, (int, float))):
        raise ValueError("Price and discount must be numbers.")
    if price < 0:
        raise ValueError("Price cannot be negative.")
    if not 0 <= discount <= 1:
        raise ValueError("Discount must be between 0 and 1.")
    return round(price * (1 - discount), 2)


def add_line_total(df):
    """
    Adds a line_total column: quantity * unit_price * (1 - discount).
    Args:
        df (pd.DataFrame): Order lines.
    Returns:
        pd.DataFrame: A copy of df with the line_total column added.
    """
    df = df.copy()
    df["line_total"] = (df["quantity"] * df["unit_price"] * (1 - df["discount"])).round(2)
    return df


def total_revenue(df):
    """
    Sums revenue across all order lines, after discounts.
    Args:
        df (pd.DataFrame): Order lines.
    Returns:
        float: Total revenue, rounded to 2 decimal places. 0.0 for no rows.
    """
    return round(float(add_line_total(df)["line_total"].sum()), 2)


def average_order_value(df):
    """
    Calculates average revenue per order (not per order line).
    Args:
        df (pd.DataFrame): Order lines.
    Returns:
        float: Average order value, rounded to 2 decimal places.
    Raises:
        ValueError: If there are no orders.
    """
    if df.empty:
        raise ValueError("No orders to average.")
    return round(total_revenue(df) / df["order_id"].nunique(), 2)


def revenue_by_category(df):
    """
    Totals revenue per product category.
    Args:
        df (pd.DataFrame): Order lines.
    Returns:
        pd.Series: Revenue per category, highest first.
    """
    totals = add_line_total(df).groupby("category")["line_total"].sum().round(2)
    return totals.sort_values(ascending=False)


def top_products(df, n=3):
    """
    Finds the products with the most units sold.
    Args:
        df (pd.DataFrame): Order lines.
        n (int): Number of products to return.
    Returns:
        pd.Series: Units sold per product, highest first.
    Raises:
        ValueError: If n is less than 1.
    """
    if n < 1:
        raise ValueError("n must be at least 1.")
    return df.groupby("product")["quantity"].sum().nlargest(n)


def monthly_revenue(df):
    """
    Totals revenue per calendar month.
    Args:
        df (pd.DataFrame): Order lines with a datetime order_date column.
    Returns:
        pd.Series: Revenue per month, indexed by "YYYY-MM", in date order.
    """
    df = add_line_total(df)
    months = df["order_date"].dt.strftime("%Y-%m")
    return df.groupby(months)["line_total"].sum().round(2).sort_index()
