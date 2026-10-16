"""Fetch MT5 candles, evaluate a simple research signal, draw a chart, and send Telegram.

Read-only: this module never submits, modifies, or closes trading orders.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from .mt5_connector import fetch_rates
from .indicators import add_indicators, crossover_signal
from .chart import make_annotated_chart
from .telegram import TelegramNotifier

TIMEFRAMES = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"}

def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Read-only MT5 analysis with annotated Telegram screenshot")
    parser.add_argument("--symbol", default="EURUSD", help="Broker symbol; may be EURUSD.a or EURUSDm")
    parser.add_argument("--timeframe", default="M15", choices=sorted(TIMEFRAMES))
    parser.add_argument("--bars", type=int, default=250)
    parser.add_argument("--chart", default="reports/latest_chart.png")
    parser.add_argument("--send-wait", action="store_true", help="Send chart even if no EMA crossover is found")
    args = parser.parse_args()
    candles = fetch_rates(args.symbol, args.timeframe, args.bars)
    df = add_indicators(candles)
    signal = crossover_signal(df)
    last = df.iloc[-1]
    entry = float(last["close"])
    atr_value = float(last["atr"]) if pd.notna(last["atr"]) else None
    setup = None
    if signal in {"BUY", "SELL"} and atr_value and atr_value > 0:
        distance = 1.5 * atr_value
        setup = {"entry": entry,
                 "stop_loss": entry - distance if signal == "BUY" else entry + distance,
                 "take_profit": entry + 2 * distance if signal == "BUY" else entry - 2 * distance}
    chart_path = make_annotated_chart(candles, args.symbol, args.timeframe, args.chart, setup)
    text = (f"{args.symbol} {args.timeframe} research alert\n"
            f"Signal: {signal}\nClose: {entry:.5f}\n"
            f"RSI(14): {last['rsi']:.1f}\nATR(14): {last['atr']:.5f}\n")
    if setup:
        text += (f"Illustrative entry: {setup['entry']:.5f}\n"
                 f"Illustrative stop loss: {setup['stop_loss']:.5f}\n"
                 f"Illustrative take profit: {setup['take_profit']:.5f}\n")
    text += "Chart includes EMA 20/50, recent range support/resistance, RSI, and levels when available. Research only; not a forecast. No orders placed."
    print(text)
    print(f"Chart saved to: {chart_path}")
    if signal in {"BUY", "SELL"} or args.send_wait:
        TelegramNotifier().send_photo(chart_path, text)
        print("Telegram chart alert sent.")
    else:
        print("No crossover: Telegram not sent. Use --send-wait to send a chart for WAIT signals too.")

if __name__ == "__main__":
    main()
