"""CLI entry point for placing Binance Futures Testnet orders."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from bot.client import BinanceAPIError, BinanceFuturesClient
from bot.logging_config import setup_logging
from bot.orders import place_order_with_summary
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)


DEFAULT_BASE_URL = "https://testnet.binancefuture.com"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Place MARKET/LIMIT/STOP orders on Binance Futures Testnet (USDT-M)."
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, help="Order side: BUY or SELL")
    parser.add_argument("--type", required=True, help="Order type: MARKET, LIMIT, or STOP")
    parser.add_argument("--quantity", required=True, help="Order quantity, e.g. 0.001")
    parser.add_argument("--price", help="Price required for LIMIT orders")
    parser.add_argument(
        "--stop-price",
        help="Stop trigger price required for STOP orders",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Binance Futures base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--log-file",
        default="logs/trading_bot.log",
        help="Path to the log file",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logger = setup_logging(args.log_file)

    try:
        api_key = os.environ["BINANCE_API_KEY"]
        api_secret = os.environ["BINANCE_API_SECRET"]
    except KeyError as exc:
        print("Failure: set BINANCE_API_KEY and BINANCE_API_SECRET environment variables.")
        logger.error("Missing environment variable: %s", exc)
        return 1

    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.type)
        quantity = validate_quantity(args.quantity)
        price = validate_price(args.price, order_type)
        stop_price = validate_stop_price(args.stop_price, order_type)
    except ValueError as exc:
        print(f"Failure: invalid input - {exc}")
        logger.error("Validation error: %s", exc)
        return 1

    client = BinanceFuturesClient(
        api_key=api_key,
        api_secret=api_secret,
        base_url=args.base_url,
        logger=logger,
    )

    request_summary = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
        "price": price if order_type in {"LIMIT", "STOP"} else "N/A",
        "stop_price": stop_price if order_type == "STOP" else "N/A",
    }
    print("Order Request Summary")
    print("---------------------")
    for key, value in request_summary.items():
        print(f"{key}: {value}")

    try:
        _, response_summary = place_order_with_summary(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except (BinanceAPIError, ConnectionError, TimeoutError, ValueError) as exc:
        print(f"\nFailure: could not place order - {exc}")
        logger.exception("Order placement failed")
        return 1
    except Exception as exc:  # pragma: no cover - defensive fallback
        print(f"\nFailure: unexpected error - {exc}")
        logger.exception("Unexpected order placement error")
        return 1

    print("\nOrder Response Details")
    print("----------------------")
    for key, value in response_summary.items():
        print(f"{key}: {value}")

    print("\nSuccess: order placed on Binance Futures Testnet.")
    return 0


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    raise SystemExit(main())

