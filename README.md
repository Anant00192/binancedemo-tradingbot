# Trading Bot for Binance Futures (Testnet)

Short Python script to place orders on the Binance Futures Testnet (USDT-M). Supports Market, Limit, and Stop-Limit orders with basic logging and validation.

## Quick Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Credentials**:
   Create a `.env` file with your testnet keys:
   ```
   BINANCE_API_KEY=your_key_here
   BINANCE_API_SECRET=your_secret_here
   BINANCE_BASE_URL=https://testnet.binancefuture.com
   ```

## Usage

Run the CLI for different order types:

*   **Market Order**: `python cli.py market --symbol BTCUSDT --side BUY --quantity 0.01`
*   **Limit Order**: `python cli.py limit --symbol BTCUSDT --side SELL --quantity 0.001 --price 150000`
*   **Stop-Limit**: `python cli.py stop-limit --symbol BTCUSDT --side BUY --quantity 0.001 --price 95000 --stop-price 94000`

## Implementation Notes

- **Client**: Hand-written wrapper for Binance REST API.
- **Validation**: Basic checks for symbol, quantity, and price.
- **Logging**: All API traffic and errors are recorded in `logs/trading_bot.log`.
- **Error Handling**: Catches network issues and Binance-specific error codes.

*Note: Developed for the Binance application task. All trades follow USDT-M rules.*
