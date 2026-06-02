"""Order placement use-case logic."""

from __future__ import annotations

from typing import Any

from bot.client import BinanceFuturesClient


def build_order_payload(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
    stop_price: str | None = None,
) -> dict[str, Any]:
    """Build Binance order request payload."""
    if order_type == "STOP":
        return {
            "algoType": "CONDITIONAL",
            "symbol": symbol,
            "side": side,
            "type": "STOP",
            "quantity": quantity,
            "timeInForce": "GTC",
            "price": price,
            "triggerPrice": stop_price,
            "newOrderRespType": "RESULT",
        }

    payload: dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
        "newOrderRespType": "RESULT",
    }
    if order_type == "LIMIT":
        payload["timeInForce"] = "GTC"
        payload["price"] = price
    return payload


def _build_response_summary(response: dict[str, Any]) -> dict[str, Any]:
    """Normalize regular and algo order responses for CLI output."""
    avg_price = response.get("avgPrice") or response.get("actualPrice")
    if str(avg_price) in {"0", "0.0", "0.00000", ""}:
        avg_price = None

    return {
        "orderId": response.get("orderId") or response.get("algoId"),
        "status": response.get("status") or response.get("algoStatus"),
        "executedQty": response.get("executedQty", "0"),
        "avgPrice": avg_price,
    }


def place_order_with_summary(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
    stop_price: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Place order and return request summary + response summary."""
    request_payload = build_order_payload(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
    )
    if order_type == "STOP":
        response = client.place_algo_order(request_payload)
    else:
        response = client.place_order(request_payload)

    order_id = response.get("orderId")
    avg_price = response.get("avgPrice")

    if order_type != "STOP" and (avg_price is None or str(avg_price) in {"0", "0.0", ""}) and order_id:
        try:
            details = client.get_order(symbol=symbol, order_id=int(order_id))
            avg_price = details.get("avgPrice", avg_price)
            response.setdefault("executedQty", details.get("executedQty"))
            response.setdefault("status", details.get("status"))
        except Exception:
            client.logger.warning("Could not enrich order response with extra details")

    response_summary = _build_response_summary(response)
    if response_summary["avgPrice"] is None and avg_price is not None:
        response_summary["avgPrice"] = avg_price
    return request_payload, response_summary

