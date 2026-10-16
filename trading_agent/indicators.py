import pandas as pd

def add_indicators(candles: pd.DataFrame) -> pd.DataFrame:
    required = {"open", "high", "low", "close"}
    missing = required - set(candles.columns)
    if missing:
        raise ValueError(f"Missing required OHLC columns: {', '.join(sorted(missing))}")
    df = candles.copy()
    for col in ("open", "high", "low", "close"):
        df[col] = pd.to_numeric(df[col], errors="raise")
    df["ema_fast"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=26, adjust=False).mean()
    delta = df["close"].diff()
    gains, losses = delta.clip(lower=0), -delta.clip(upper=0)
    avg_gain = gains.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    df["rsi"] = 100 - (100 / (1 + rs))
    previous_close = df["close"].shift(1)
    tr = pd.concat([df["high"]-df["low"], (df["high"]-previous_close).abs(),
                    (df["low"]-previous_close).abs()], axis=1).max(axis=1)
    df["atr"] = tr.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    return df

def crossover_signal(df: pd.DataFrame) -> str:
    if len(df) < 2:
        return "WAIT"
    previous, current = df.iloc[-2], df.iloc[-1]
    if pd.isna(previous["ema_fast"]) or pd.isna(current["ema_slow"]):
        return "WAIT"
    if previous["ema_fast"] <= previous["ema_slow"] and current["ema_fast"] > current["ema_slow"]:
        return "BUY"
    if previous["ema_fast"] >= previous["ema_slow"] and current["ema_fast"] < current["ema_slow"]:
        return "SELL"
    return "WAIT"
