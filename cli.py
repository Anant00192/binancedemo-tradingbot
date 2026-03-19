#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Testnet trading bot.

Usage:
    python cli.py market  --symbol BTCUSDT --side BUY  --quantity 0.001
    python cli.py limit   --symbol ETHUSDT --side SELL --quantity 0.05 --price 3500
    python cli.py stop-limit --symbol BTCUSDT --side BUY --quantity 0.001 --price 95000 --stop-price 94000
"""

import argparse
import sys
import os

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from bot.logging_config import setup_logging
from bot.client import BinanceClient, BinanceAPIError
from bot.orders import place_market_order, place_limit_order, place_stop_limit_order
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
)

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place orders on Binance Futures Testnet (USDT-M).",
    )
    subparsers = parser.add_subparsers(dest="command", help="Order type")

    # --- market ---
    sp_market = subparsers.add_parser("market", help="Place a market order")
    sp_market.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    sp_market.add_argument("--side", required=True, help="BUY or SELL")
    sp_market.add_argument("--quantity", required=True, type=float, help="Order quantity")

    # --- limit ---
    sp_limit = subparsers.add_parser("limit", help="Place a limit order")
    sp_limit.add_argument("--symbol", required=True)
    sp_limit.add_argument("--side", required=True)
    sp_limit.add_argument("--quantity", required=True, type=float)
    sp_limit.add_argument("--price", required=True, type=float, help="Limit price")

    # --- stop-limit ---
    sp_stop = subparsers.add_parser("stop-limit", help="Place a stop-limit order")
    sp_stop.add_argument("--symbol", required=True)
    sp_stop.add_argument("--side", required=True)
    sp_stop.add_argument("--quantity", required=True, type=float)
    sp_stop.add_argument("--price", required=True, type=float, help="Limit price")
    sp_stop.add_argument("--stop-price", required=True, type=float, help="Trigger / stop price")

    return parser


def print_request_summary(args):
    """Show the user what we're about to send."""
    table = Table(title="Order Request", show_header=False, border_style="cyan")
    table.add_column("Field", style="bold")
    table.add_column("Value")

    table.add_row("Command", args.command)
    table.add_row("Symbol", args.symbol)
    table.add_row("Side", args.side)
    table.add_row("Quantity", str(args.quantity))
    if hasattr(args, "price") and args.price is not None:
        table.add_row("Price", str(args.price))
    if hasattr(args, "stop_price") and args.stop_price is not None:
        table.add_row("Stop Price", str(args.stop_price))

    console.print(table)


def print_response(result: dict, success: bool):
    """Pretty-print the order response."""
    if success:
        console.print("\n[bold green]✓ Order placed successfully![/bold green]\n")
    else:
        console.print("\n[bold red]✗ Order failed.[/bold red]\n")
        return

    table = Table(title="Order Response", show_header=False, border_style="green")
    table.add_column("Field", style="bold")
    table.add_column("Value")

    for key, val in result.items():
        table.add_row(key, str(val))

    console.print(table)


def main():
    load_dotenv()
    logger = setup_logging()

    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # --- grab credentials ---
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    base_url = os.getenv("BINANCE_BASE_URL", "https://testnet.binancefuture.com")

    if not api_key or not api_secret:
        console.print("[bold red]Error:[/bold red] BINANCE_API_KEY and BINANCE_API_SECRET must be set in .env")
        sys.exit(1)

    # --- validate inputs ---
    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        quantity = validate_quantity(args.quantity)

        price = None
        stop_price = None

        if args.command == "limit":
            order_type = validate_order_type("LIMIT")
            price = validate_price(args.price, "LIMIT")

        elif args.command == "stop-limit":
            order_type = validate_order_type("STOP")
            price = validate_price(args.price, "STOP")
            stop_price = validate_stop_price(args.stop_price, "STOP")

        else:
            order_type = validate_order_type("MARKET")

    except ValueError as e:
        console.print(f"[bold red]Validation error:[/bold red] {e}")
        logger.error(f"Validation failed: {e}")
        sys.exit(1)

    # --- show request summary ---
    print_request_summary(args)

    # --- place the order ---
    client = BinanceClient(api_key, api_secret, base_url)

    try:
        if args.command == "market":
            result = place_market_order(client, symbol, side, quantity)

        elif args.command == "limit":
            result = place_limit_order(client, symbol, side, quantity, price)

        elif args.command == "stop-limit":
            result = place_stop_limit_order(client, symbol, side, quantity, price, stop_price)

        print_response(result, success=True)

    except BinanceAPIError as e:
        logger.error(f"API error: {e}")
        console.print(f"[bold red]API Error:[/bold red] {e}")
        sys.exit(1)

    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        console.print(f"[bold red]Network Error:[/bold red] {e}")
        sys.exit(1)

    except Exception as e:
        logger.exception("Unexpected error during order placement")
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
