import argparse
from pathlib import Path
import pandas as pd
from .indicators import add_indicators, crossover_signal
from .backtest import run_backtest
from .risk import position_size_units
from .notifier import send_telegram

def main():
    parser = argparse.ArgumentParser(description="Analyze forex candles and backtest a demo EMA strategy.")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--balance", type=float, default=1000)
    parser.add_argument("--risk-pct", type=float, default=0.5)
    parser.add_argument("--stop-pct", type=float, default=0.005)
    parser.add_argument("--target-pct", type=float, default=0.01)
    parser.add_argument("--notify", action="store_true")
    args = parser.parse_args()
    path = Path(args.csv)
    if not path.exists():
        parser.error(f"CSV file not found: {path}")
    candles = pd.read_csv(path)
    df = add_indicators(candles)
    signal, last = crossover_signal(df), df.iloc[-1]
    result = run_backtest(candles, args.stop_pct, args.target_pct, args.balance, args.risk_pct)
    loss = "N/A" if result.loss_rate is None else f"{result.loss_rate:.1%}"
    win = "N/A" if result.win_rate is None else f"{result.win_rate:.1%}"
    message = (f"{args.symbol} research alert\nSignal: {signal}\nClose: {last.close:.5f}\n"
               f"RSI(14): {last.rsi:.1f}\nATR(14): {last.atr:.5f}\n"
               f"Backtest trades: {len(result.trades)}\nHistorical loss rate: {loss}\n"
               f"Historical win rate: {win}\nHistorical rates are not forecasts.")
    print(message)
    if signal in {"BUY", "SELL"} and pd.notna(last.atr):
        entry = float(last.close)
        stop = entry - float(last.atr)*1.5 if signal == "BUY" else entry + float(last.atr)*1.5
        units = position_size_units(args.balance, args.risk_pct, entry, stop)
        print(f"Illustrative position size: {units:.2f} units; verify broker contract specifications.")
    if args.notify:
        send_telegram(message)
        print("Telegram notification sent.")

if __name__ == "__main__":
    main()
