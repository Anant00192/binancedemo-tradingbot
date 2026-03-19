# Binance Futures Testnet Trading Bot

A command-line trading bot for placing orders on Binance Futures Testnet (USDT-M).
Supports **Market**, **Limit**, and **Stop-Limit** orders with input validation, structured logging, and clean error handling.

## Prerequisites

- Python 3.10+
- A [Binance Futures Testnet](https://testnet.binancefuture.com) account with API credentials

## Setup

1. **Clone the repo and cd into it:**

```bash
git clone https://github.com/Anant00192/binancedemo-tradingbot.git
cd binancedemo-tradingbot
```

2. **Create a virtual environment (recommended):**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Configure API credentials:**

Copy the example env file and fill in your testnet keys:

```bash
cp .env.example .env
```

Then edit `.env`:

```
BINANCE_API_KEY=<your_testnet_api_key>
BINANCE_API_SECRET=<your_testnet_api_secret>
BINANCE_BASE_URL=https://testnet.binancefuture.com
```

## Usage

The bot uses subcommands for different order types.

### Market Order

```bash
python cli.py market --symbol BTCUSDT --side BUY --quantity 0.001
```

### Limit Order

```bash
python cli.py limit --symbol BTCUSDT --side SELL --quantity 0.001 --price 150000
```

### Stop-Limit Order (Bonus)

```bash
python cli.py stop-limit --symbol BTCUSDT --side BUY --quantity 0.001 --price 95000 --stop-price 94000
```

### Help

```bash
python cli.py --help
python cli.py market --help
```

## Output

For each order the CLI prints:

1. **Request summary** — what you're about to send (symbol, side, qty, price)
2. **Response details** — `orderId`, `status`, `executedQty`, `avgPrice`, etc.
3. **Success / failure message** with colour-coded output

## Logging

All API requests, responses, and errors are logged to `logs/trading_bot.log`.
The log file rotates automatically at 5 MB (keeps 3 backups).

Check recent log entries:

```bash
# Windows
type logs\trading_bot.log
# Linux / macOS
tail -f logs/trading_bot.log
```

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py           # Binance REST client (auth, signing, error mapping)
│   ├── orders.py            # Order placement functions
│   ├── validators.py        # Input validation helpers
│   └── logging_config.py    # Logging configuration
├── cli.py                   # CLI entry point (argparse)
├── logs/                    # Auto-created at runtime
├── .env.example             # Template for API credentials
├── .gitignore
├── requirements.txt
└── README.md
```

## Assumptions

- All orders target the **USDT-M Futures Testnet** at `https://testnet.binancefuture.com`.
- The bot does **not** manage position sizing, leverage, or margin — it simply places orders as instructed.
- Symbol validation is intentionally soft (warning-only) since testnet symbols can change.
- `timeInForce` defaults to `GTC` (Good Till Cancelled) for Limit and Stop-Limit orders.
- The `STOP` order type maps to Binance's `STOP` type which behaves as a stop-limit order (requires both `price` and `stopPrice`).
