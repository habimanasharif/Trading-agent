from dataclasses import dataclass
import pandas as pd
from .indicators import add_indicators

@dataclass
class BacktestResult:
    trades: list[dict]
    starting_balance: float
    ending_balance: float

    @property
    def loss_rate(self):
        return None if not self.trades else sum(t["outcome"] == "LOSS" for t in self.trades) / len(self.trades)

    @property
    def win_rate(self):
        return None if not self.trades else sum(t["outcome"] == "WIN" for t in self.trades) / len(self.trades)

def run_backtest(candles: pd.DataFrame, stop_pct: float = 0.005, take_profit_pct: float = 0.01,
                 starting_balance: float = 1000.0, risk_pct: float = 0.5) -> BacktestResult:
    """Example EMA crossover backtest. Omits costs; demo/research use only."""
    if stop_pct <= 0 or take_profit_pct <= 0:
        raise ValueError("stop_pct and take_profit_pct must be positive")
    df = add_indicators(candles).reset_index(drop=True)
    trades, balance, position = [], float(starting_balance), None
    for i in range(2, len(df) - 1):
        row, prev, next_row = df.iloc[i], df.iloc[i-1], df.iloc[i+1]
        signal = None
        if prev.ema_fast <= prev.ema_slow and row.ema_fast > row.ema_slow:
            signal = "BUY"
        elif prev.ema_fast >= prev.ema_slow and row.ema_fast < row.ema_slow:
            signal = "SELL"
        if position:
            if position["side"] == "BUY":
                sl_hit, tp_hit = row.low <= position["stop"], row.high >= position["target"]
            else:
                sl_hit, tp_hit = row.high >= position["stop"], row.low <= position["target"]
            outcome = "LOSS" if sl_hit else ("WIN" if tp_hit else None)
            if outcome:
                exit_price = position["stop"] if outcome == "LOSS" else position["target"]
                risk_cash = balance * risk_pct / 100
                pnl = -risk_cash if outcome == "LOSS" else risk_cash * take_profit_pct / stop_pct
                balance += pnl
                trades.append({"side": position["side"], "entry": position["entry"],
                               "exit": float(exit_price), "outcome": outcome, "pnl": pnl})
                position = None
        if position is None and signal:
            entry = float(next_row.open)
            if signal == "BUY":
                stop, target = entry * (1-stop_pct), entry * (1+take_profit_pct)
            else:
                stop, target = entry * (1+stop_pct), entry * (1-take_profit_pct)
            position = {"side": signal, "entry": entry, "stop": stop, "target": target}
    return BacktestResult(trades, starting_balance, balance)
