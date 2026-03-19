"""
Order placement functions.
Each one builds the correct param dict and delegates to the client.
"""

import logging
from bot.client import BinanceClient

logger = logging.getLogger("trading_bot")


def _extract_result(raw: dict) -> dict:
    """Pull the fields we care about from the API response."""
    return {
        "orderId": raw.get("orderId"),
        "symbol": raw.get("symbol"),
        "side": raw.get("side"),
        "type": raw.get("type"),
        "status": raw.get("status"),
        "origQty": raw.get("origQty"),
        "executedQty": raw.get("executedQty"),
        "avgPrice": raw.get("avgPrice", "N/A"),
        "price": raw.get("price", "N/A"),
    }


def place_market_order(client: BinanceClient, symbol: str, side: str, quantity: float) -> dict:
    logger.info(f"Placing MARKET {side} order: {quantity} {symbol}")
    raw = client.place_order(
        symbol=symbol,
        side=side,
        type="MARKET",
        quantity=quantity,
    )
    result = _extract_result(raw)
    logger.info(f"MARKET order placed — orderId={result['orderId']}, status={result['status']}")
    return result


def place_limit_order(client: BinanceClient, symbol: str, side: str, quantity: float, price: float) -> dict:
    logger.info(f"Placing LIMIT {side} order: {quantity} {symbol} @ {price}")
    raw = client.place_order(
        symbol=symbol,
        side=side,
        type="LIMIT",
        quantity=quantity,
        price=price,
        timeInForce="GTC",
    )
    result = _extract_result(raw)
    logger.info(f"LIMIT order placed — orderId={result['orderId']}, status={result['status']}")
    return result


def place_stop_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    stop_price: float,
) -> dict:
    logger.info(f"Placing STOP_LIMIT {side} order: {quantity} {symbol} @ {price}, stop={stop_price}")
    raw = client.place_order(
        symbol=symbol,
        side=side,
        type="STOP",
        quantity=quantity,
        price=price,
        stopPrice=stop_price,
        timeInForce="GTC",
    )
    result = _extract_result(raw)
    logger.info(f"STOP order placed — orderId={result['orderId']}, status={result['status']}")
    return result
