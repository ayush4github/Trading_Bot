"""Validation helpers for CLI inputs."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP"}


def validate_symbol(symbol: str) -> str:
    """Validate trading symbol format."""
    clean = symbol.strip().upper()
    if not clean.isalnum() or len(clean) < 6:
        raise ValueError("Symbol must be alphanumeric, e.g. BTCUSDT.")
    return clean


def validate_side(side: str) -> str:
    """Validate order side."""
    clean = side.strip().upper()
    if clean not in VALID_SIDES:
        raise ValueError(f"Invalid side '{side}'. Use BUY or SELL.")
    return clean


def validate_order_type(order_type: str) -> str:
    """Validate order type."""
    clean = order_type.strip().upper()
    if clean not in VALID_ORDER_TYPES:
        raise ValueError("Invalid order type. Use MARKET, LIMIT, or STOP.")
    return clean


def _to_positive_decimal(raw: str, field_name: str) -> str:
    """Convert numeric string to positive decimal string."""
    try:
        value = Decimal(raw)
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(f"{field_name} must be a valid number.") from exc

    if value <= 0:
        raise ValueError(f"{field_name} must be greater than 0.")
    return format(value.normalize(), "f")


def validate_quantity(quantity: str) -> str:
    """Validate quantity as positive decimal string."""
    return _to_positive_decimal(quantity, "Quantity")


def validate_price(price: str | None, order_type: str) -> str | None:
    """Validate price requirement and format."""
    if order_type in {"LIMIT", "STOP"}:
        if price is None:
            raise ValueError("Price is required for LIMIT and STOP orders.")
        return _to_positive_decimal(price, "Price")
    return None


def validate_stop_price(stop_price: str | None, order_type: str) -> str | None:
    """Validate stop price requirement and format."""
    if order_type == "STOP":
        if stop_price is None:
            raise ValueError("Stop price is required for STOP orders.")
        return _to_positive_decimal(stop_price, "Stop price")
    return None

