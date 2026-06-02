# Binance Futures Testnet Trading Bot

Python CLI for placing orders on Binance Futures Testnet (USDT-M) via signed REST API calls.

Supports MARKET and LIMIT orders (required), plus STOP as a bonus order type.

## Project Structure

```text
bot/
  client.py          # Binance API client
  orders.py          # Order placement logic
  validators.py      # Input validation
  logging_config.py
cli.py               # CLI entry point
logs/
  market_order.log
  limit_order.log
requirements.txt
```

## Setup

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Set testnet credentials:

```powershell
$env:BINANCE_API_KEY="your_testnet_api_key"
$env:BINANCE_API_SECRET="your_testnet_api_secret"
```

## Usage

Base URL (default): `https://testnet.binancefuture.com`

MARKET order:

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

LIMIT order:

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 120000
```

STOP order (bonus):

```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.001 --price 68000 --stop-price 68500
```

Optional flags: `--base-url`, `--log-file`, `--stop-price`

## Output

The CLI prints an order request summary, response details (`orderId`, `status`, `executedQty`, `avgPrice`), and a success/failure message.

Runtime logs are written to `logs/trading_bot.log`.

## Assumptions

- Valid Binance Futures Testnet account and API credentials are required.
- Quantity and price precision are validated by Binance; this app checks required fields and positive numeric values.
- `avgPrice` may be unavailable for unfilled orders.
- STOP orders use Binance Algo Order API (`/fapi/v1/algoOrder`) with `algoType=CONDITIONAL`.
