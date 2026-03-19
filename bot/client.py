# Binance Futures REST client with HMAC signing

import hashlib
import hmac
import time
import logging

import requests

logger = logging.getLogger("trading_bot")


class BinanceAPIError(Exception):
    # Error response from Binance

    def __init__(self, status_code, code, msg):
        self.status_code = status_code
        self.code = code
        self.msg = msg
        super().__init__(f"Binance API error {code}: {msg} (HTTP {status_code})")


class BinanceClient:
    """
    Minimal client for Binance Futures (USDT-M) testnet.
    Only covers order placement — extend as needed.
    """

    ORDER_ENDPOINT = "/fapi/v1/order"

    def __init__(self, api_key: str, api_secret: str, base_url: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")

        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
        })

    # ---- internal helpers ----

    def _timestamp(self):
        return int(time.time() * 1000)

    def _request(self, method, endpoint, params=None):
        url = self.base_url + endpoint
        params = params or {}
        params["timestamp"] = self._timestamp()

        # 1. Build query string (sorted keys for consistency)
        query_parts = [f"{k}={v}" for k, v in sorted(params.items())]
        query_string = "&".join(query_parts)

        # 2. Generate HMAC SHA256 signature
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        # 3. Append signature to query string
        full_query = f"{query_string}&signature={signature}"
        full_url = f"{url}?{full_query}"

        # log outgoing request (redact signature in log)
        logger.debug(f"Request {method} {url}?{query_string}&signature=...")

        try:
            resp = self.session.request(method, full_url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as exc:
            # If we have a response, it might be a Binance error (code < 0)
            if hasattr(exc, "response") and exc.response is not None:
                try:
                    data = exc.response.json()
                    code = data.get("code", exc.response.status_code)
                    msg = data.get("msg", "Unknown error")
                    logger.error(f"API Error [{exc.response.status_code}]: {msg} (code {code})")
                    raise BinanceAPIError(exc.response.status_code, code, msg) from exc
                except ValueError:
                    pass
            
            logger.error(f"Network error: {exc}")
            raise ConnectionError(f"Could not reach Binance API: {exc}") from exc

        data = resp.json()
        logger.debug(f"Response [{resp.status_code}]: {data}")

        # Some errors might still come back with 200 OK but a negative code
        if "code" in data and int(data["code"]) < 0:
            raise BinanceAPIError(resp.status_code, data["code"], data["msg"])

        return data

    # ---- public methods ----

    def place_order(self, **kwargs) -> dict:
        """Send a new order to the futures testnet.

        Pass parameters exactly as the Binance docs expect them,
        e.g. symbol, side, type, quantity, price, timeInForce, etc.
        """
        return self._request("POST", self.ORDER_ENDPOINT, kwargs)

    def server_time(self) -> dict:
        """Quick connectivity check — returns {'serverTime': <epoch_ms>}."""
        return self._request("GET", "/fapi/v1/time")
