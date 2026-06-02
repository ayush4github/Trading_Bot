"""Binance Futures Testnet API client."""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import requests


class BinanceAPIError(Exception):
    """Raised when Binance API returns an error response."""


class BinanceFuturesClient:
    """Minimal Binance USDT-M futures client with signed requests."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str,
        logger: Any,
        timeout: float = 10.0,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def _sign(self, query_string: str) -> str:
        return hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _request(self, method: str, path: str, params: dict[str, Any], signed: bool) -> dict[str, Any]:
        payload = dict(params)

        if signed:
            payload["timestamp"] = int(time.time() * 1000)
            payload["recvWindow"] = 5000
            query_string = urlencode(payload, doseq=True)
            payload["signature"] = self._sign(query_string)

        url = f"{self.base_url}{path}"
        log_payload = dict(payload)
        if "signature" in log_payload:
            log_payload["signature"] = "***"
        self.logger.info("API request | method=%s url=%s payload=%s", method, url, log_payload)

        try:
            if method.upper() == "POST":
                response = self.session.post(url, params=payload, timeout=self.timeout)
            elif method.upper() == "GET":
                response = self.session.get(url, params=payload, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported method '{method}'.")
        except requests.RequestException as exc:
            self.logger.exception("Network error while calling Binance API")
            raise ConnectionError(f"Network failure: {exc}") from exc

        raw_text = response.text
        self.logger.info("API response | status=%s body=%s", response.status_code, raw_text)

        try:
            data = response.json()
        except ValueError as exc:
            raise BinanceAPIError(
                f"Unexpected non-JSON response (status {response.status_code}): {raw_text}"
            ) from exc

        if response.status_code >= 400:
            message = data.get("msg", "Unknown API error")
            code = data.get("code", "N/A")
            raise BinanceAPIError(f"Binance API error {code}: {message}")

        return data

    def place_order(self, params: dict[str, Any]) -> dict[str, Any]:
        """Place a signed futures order."""
        return self._request("POST", "/fapi/v1/order", params=params, signed=True)

    def place_algo_order(self, params: dict[str, Any]) -> dict[str, Any]:
        """Place a signed conditional (algo) futures order."""
        return self._request("POST", "/fapi/v1/algoOrder", params=params, signed=True)

    def get_order(self, symbol: str, order_id: int) -> dict[str, Any]:
        """Fetch order details for additional fields like avgPrice."""
        params = {"symbol": symbol, "orderId": order_id}
        return self._request("GET", "/fapi/v1/order", params=params, signed=True)

