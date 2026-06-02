# Simplified Trading Bot - Binance Futures Testnet

This project is a Python CLI app that places **MARKET**, **LIMIT**, and **STOP (Stop-Limit style)** orders on Binance Futures Testnet (USDT-M) using signed REST API requests.

## Features
- Places `MARKET`, `LIMIT`, and `STOP` orders
- Supports both `BUY` and `SELL`
- Validates CLI input (`symbol`, `side`, `type`, `quantity`, `price`, `stop-price`)
- Structured modules (`client`, `orders`, `validators`, `logging_config`, `cli`)
- Logs requests, responses, and errors to file
- Handles validation errors, API failures, and network failures

## Project Structure
```text
trading_bot/
  bot/
    __init__.py
    client.py
    orders.py
    validators.py
    logging_config.py
  logs/
    market_order_example.log
    limit_order_example.log
  cli.py
  README.md
  requirements.txt
```

## Setup
1. Create and activate a virtual environment:
   - Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set Binance testnet credentials:
   - Windows (PowerShell):
     ```powershell
     $env:BINANCE_API_KEY="your_testnet_api_key"
     $env:BINANCE_API_SECRET="your_testnet_api_secret"
     ```

## Binance Base URL
This app defaults to:
`https://testnet.binancefuture.com`

You can override it via `--base-url` if needed.

## Usage

### 1) MARKET order example
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### 2) LIMIT order example
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 80000
```

### 3) STOP order example (bonus)
Binance routes conditional STOP orders through the Algo Order API (`/fapi/v1/algoOrder`).

Use a trigger below current price for a SELL stop-loss style order:
```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.001 --price 68000 --stop-price 68500
```

### Optional arguments
- `--base-url` (default is Binance futures testnet URL)
- `--log-file` (default `logs/trading_bot.log`)
- `--stop-price` (required for `STOP`)

## Output
The CLI prints:
- Order request summary
- Order response details:
  - `orderId`
  - `status`
  - `executedQty`
  - `avgPrice` (when available)
- Final success/failure message

## Logs
- Runtime logs are written to `logs/trading_bot.log`
- Included sample logs for submission:
  - `logs/market_order_example.log`
  - `logs/limit_order_example.log`

## Assumptions
- User has an active Binance Futures Testnet account and valid API credentials.
- Quantity/price precision and min/max filters are validated by Binance server-side (this app validates numeric positivity and required fields).
- `avgPrice` may be unavailable immediately for some order states and can remain `None` or `0`.
- For `STOP`, this app uses Binance Algo Order API with `algoType=CONDITIONAL`, `type=STOP`, `price`, and `triggerPrice`.

