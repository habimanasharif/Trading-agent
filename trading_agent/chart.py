"""Create annotated candlestick screenshots for Telegram using matplotlib."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def make_annotated_chart(candles: pd.DataFrame, symbol: str, timeframe: str,
                         output_path: str | Path, signal: dict | None = None,
                         max_bars: int = 100) -> Path:
    """Render candles, EMAs, local support/resistance, RSI, and optional trade levels.

    This generates a separate chart image; it does not alter the live MT5 chart window.
    Candles must contain open/high/low/close and may contain timestamp.
    """
    required = {"open", "high", "low", "close"}
    if not required.issubset(candles.columns):
        raise ValueError(f"Candles must contain columns: {sorted(required)}")
    df = candles.tail(max_bars).copy().reset_index(drop=True)
    if len(df) < 20:
        raise ValueError("At least 20 candles are required to draw a useful chart")
    closes = df["close"].astype(float)
    df["ema20"] = closes.ewm(span=20, adjust=False).mean()
    df["ema50"] = closes.ewm(span=50, adjust=False).mean()
    delta = closes.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = gain / loss.replace(0, float("nan"))
    df["rsi14"] = 100 - (100 / (1 + rs))
    prev_close = closes.shift(1)
    tr = pd.concat([df["high"]-df["low"], (df["high"]-prev_close).abs(),
                    (df["low"]-prev_close).abs()], axis=1).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    fig, (ax, rax) = plt.subplots(2, 1, figsize=(13, 8), sharex=True,
                                  gridspec_kw={"height_ratios": [3, 1]})
    fig.subplots_adjust(hspace=0.08, top=0.90, bottom=0.11, left=0.08, right=0.97)
    width = 0.62
    for i, row in df.iterrows():
        up = float(row.close) >= float(row.open)
        body_bottom = min(float(row.open), float(row.close))
        body_height = max(abs(float(row.close) - float(row.open)), 1e-8)
        # Keep default matplotlib colors, so chart remains theme-neutral.
        candle_color = "#16856b" if up else "#d14b4b"
        ax.vlines(i, float(row.low), float(row.high), color=candle_color, linewidth=1)
        ax.add_patch(Rectangle((i-width/2, body_bottom), width, body_height,
                               facecolor=candle_color, edgecolor=candle_color, linewidth=0.7))
    ax.plot(df.index, df.ema20, label="EMA 20", linewidth=1.2)
    ax.plot(df.index, df.ema50, label="EMA 50", linewidth=1.2)
    # Simple, transparent local swing levels; not a guarantee of future support/resistance.
    support = float(df.low.tail(40).min())
    resistance = float(df.high.tail(40).max())
    ax.axhline(support, linestyle="--", linewidth=1, label=f"Recent support {support:.5f}")
    ax.axhline(resistance, linestyle="--", linewidth=1, label=f"Recent resistance {resistance:.5f}")
    if signal:
        for key, label in (("entry", "Entry"), ("stop_loss", "Stop loss"), ("take_profit", "Take profit")):
            val = signal.get(key)
            if val is not None:
                ax.axhline(float(val), linestyle=":" if key == "entry" else "--", linewidth=1.5,
                           label=f"{label} {float(val):.5f}")
    ax.set_title(f"{symbol} · {timeframe} · Technical analysis (illustrative, not a forecast)")
    ax.set_ylabel("Price")
    ax.grid(True, alpha=0.2)
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    rax.plot(df.index, df.rsi14, label="RSI 14", linewidth=1.2)
    rax.axhline(70, linestyle="--", linewidth=0.8)
    rax.axhline(30, linestyle="--", linewidth=0.8)
    rax.set_ylim(0, 100)
    rax.set_ylabel("RSI")
    rax.set_xlabel("Candle index (oldest → newest)")
    rax.grid(True, alpha=0.2)
    if "timestamp" in df.columns:
        # Sparse readable timestamp ticks.
        positions = list(range(0, len(df), max(1, len(df)//6)))
        labels = [str(df.iloc[p]["timestamp"])[:16] for p in positions]
        rax.set_xticks(positions, labels, rotation=20, ha="right", fontsize=8)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return out
