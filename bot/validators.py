# CLI input validation

SUPPORTED_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT",
    "DOGEUSDT", "SOLUSDT", "ADAUSDT", "LTCUSDT",
]

VALID_SIDES = ("BUY", "SELL")
VALID_ORDER_TYPES = ("MARKET", "LIMIT", "STOP")


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    # we don't hard-block unknown symbols, just warn
    if symbol not in SUPPORTED_SYMBOLS:
        import logging
        logging.getLogger("trading_bot").warning(
            f"Symbol '{symbol}' is not in the common list — double check it exists on the testnet."
        )
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Side must be one of {VALID_SIDES}, got '{side}'.")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    # allow user-friendly aliases
    aliases = {"STOP-LIMIT": "STOP", "STOPLIMIT": "STOP", "STOP_LIMIT": "STOP"}
    order_type = aliases.get(order_type, order_type)
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(f"Order type must be one of {VALID_ORDER_TYPES}, got '{order_type}'.")
    return order_type


def validate_quantity(qty) -> float:
    try:
        qty = float(qty)
    except (TypeError, ValueError):
        raise ValueError(f"Quantity must be a number, got '{qty}'.")
    if qty <= 0:
        raise ValueError(f"Quantity must be positive, got {qty}.")
    return qty


def validate_price(price, order_type: str) -> float | None:
    """Price is mandatory for LIMIT and STOP orders."""
    if order_type in ("LIMIT", "STOP"):
        if price is None:
            raise ValueError(f"Price is required for {order_type} orders.")
        try:
            price = float(price)
        except (TypeError, ValueError):
            raise ValueError(f"Price must be a number, got '{price}'.")
        if price <= 0:
            raise ValueError(f"Price must be positive, got {price}.")
        return price
    return None  # not needed for MARKET


def validate_stop_price(stop_price, order_type: str) -> float | None:
    """Stop price is only needed for STOP (stop-limit) orders."""
    if order_type == "STOP":
        if stop_price is None:
            raise ValueError("Stop price (--stop-price) is required for STOP orders.")
        try:
            stop_price = float(stop_price)
        except (TypeError, ValueError):
            raise ValueError(f"Stop price must be a number, got '{stop_price}'.")
        if stop_price <= 0:
            raise ValueError(f"Stop price must be positive, got {stop_price}.")
        return stop_price
    return None
