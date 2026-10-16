# Local MT5 Forex Trading Agent — alerts only

A research-first Python starter for MetaTrader 5 (MT5). It reads completed candles, calculates EMA/RSI/ATR, produces a simple EMA crossover research signal, and can generate an annotated chart image and send it to Telegram. **It does not place or manage trades.**

> **Risk notice:** This is educational software, not financial advice. The included EMA crossover is an unvalidated example, not a profitable strategy guarantee. No win rate or accuracy target is promised. Test with historical data and a demo account before risking money.

## Features

- CSV-based indicator analysis and a simple historical backtest.
- Optional read-only MT5 candle connection (MetaTrader5 Python package is generally supported on Windows).
- Annotated PNG charts with candlesticks, EMA 20/50, recent-range support/resistance, RSI, and entry/stop/target levels when a crossover signal exists.
- Optional Telegram photo alert, using a Telegram bot token and chat ID.
- No order-placement code or automatic execution.

The screenshot is a **separate Python-rendered chart**, not a screenshot of the actual MT5 terminal. It visualizes candles fetched from MT5. The support/resistance shown is a simple recent-range approximation, not an advanced market-structure detector.

## 1. Install

Use Python 3.11+ in a virtual environment:

```powershell
# Windows PowerShell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

For macOS/Linux, use `python3 -m venv .venv`, `source .venv/bin/activate`, and `cp .env.example .env`. CSV mode works cross-platform. The official MT5 Python integration generally requires Windows and an installed MT5 desktop terminal; if using MT5 mode, install the `MetaTrader5` package on a supported Windows Python setup:

```powershell
pip install MetaTrader5
```

Open MT5, log in to your broker's account, and make sure the desired symbol and history are available. Broker symbols can include suffixes, such as `EURUSDm`.

## 2. Configure Telegram (optional)

1. Create a bot using Telegram's official `@BotFather`.
2. Start a chat with your bot and obtain your chat ID (for a private chat, send a message to the bot first).
3. Put the values in `.env`:

```dotenv
TELEGRAM_BOT_TOKEN=put_your_bot_token_here
TELEGRAM_CHAT_ID=put_your_chat_id_here
```

Never commit `.env`, bot tokens, broker passwords, or account details. Do not share your token with anyone.

## 3. Run the MT5 → chart → Telegram workflow

With MT5 open and Telegram configured:

```powershell
python -m trading_agent.mt5_alerts --symbol EURUSD --timeframe M15 --bars 250
```

This fetches completed candles, calculates the sample crossover signal, saves `reports/latest_chart.png`, and sends an annotated chart to Telegram when a BUY/SELL crossover is detected. To send a chart even when the result is WAIT:

```powershell
python -m trading_agent.mt5_alerts --symbol EURUSD --timeframe M15 --send-wait
```

For a broker-specific symbol:

```powershell
python -m trading_agent.mt5_alerts --symbol EURUSD.a --timeframe H1
```

Run the command again whenever you want a new analysis. This starter does not yet run a continuous polling loop or scheduled task. Your computer, internet, MT5 terminal, and Python process need to be running for live monitoring.

## 4. Run from CSV (cross-platform)

Create `data/EURUSD.csv` with columns `timestamp,open,high,low,close` using historical candles:

```powershell
python -m trading_agent.cli --csv data/EURUSD.csv --symbol EURUSD --balance 1000 --risk-pct 0.5
```

## 5. Tests

```powershell
pytest
```

## Known limitations

- EMA crossover signals are a baseline example only and can be unprofitable.
- The MT5 workflow currently alerts only on the sample crossover, not on an optimized or validated strategy.
- Entry/stop/target levels are illustrative ATR-based levels; they do not account for broker contract size, spread, slippage, commission, gaps, or news events.
- The backtest is simplified and is not a guarantee of live results.
- The screenshot is a Python-rendered chart; it does not draw objects onto the MT5 terminal itself.
- MT5 data availability depends on terminal history settings and broker symbol names.
