"""Read-only MetaTrader 5 market-data connector. No order functions are exposed."""
from __future__ import annotations

from datetime import datetime, timezone
import pandas as pd


def fetch_rates(symbol: str = "EURUSD", timeframe: str = "M15", bars: int = 250) -> pd.DataFrame:
    """Fetch completed candles from an already installed/running MT5 terminal.

    Requires the MetaTrader5 Python package (normally Windows) and a logged-in MT5 terminal.
    The newest, still-forming candle is excluded.
    """
    try:
        import MetaTrader5 as mt5
    except ImportError as exc:
        raise RuntimeError("MetaTrader5 package missing. Install it on a supported Windows setup.") from exc

    timeframes = {
        "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30, "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1,
    }
    if timeframe not in timeframes:
        raise ValueError(f"Unsupported timeframe: {timeframe}")
    if not mt5.initialize():
        raise RuntimeError(f"Could not connect to MT5: {mt5.last_error()}")
    try:
        if not mt5.symbol_select(symbol, True):
            raise RuntimeError(f"Could not select symbol {symbol}: {mt5.last_error()}")
        # start_pos=1 skips the current, unfinished candle.
        rates = mt5.copy_rates_from_pos(symbol, timeframes[timeframe], 1, bars)
        if rates is None or len(rates) < 50:
            raise RuntimeError(f"Not enough candle history for {symbol}. Check MT5 history settings.")
        frame = pd.DataFrame(rates)
        frame["timestamp"] = pd.to_datetime(frame["time"], unit="s", utc=True)
        return frame[["timestamp", "open", "high", "low", "close", "tick_volume"]].reset_index(drop=True)
    finally:
        mt5.shutdown()
