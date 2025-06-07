# data_utils_beginner.py

import pandas as pd
import os
from ta.trend import EMAIndicator
from ta.volume import VolumeWeightedAveragePrice

def load_data(ticker, interval, data_dir="data/fixed"):
    filename = f"{ticker.upper()}_{interval}.csv"
    path = os.path.join(data_dir, filename)
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    df.columns = [col.strip().capitalize() for col in df.columns]
    df = df.apply(pd.to_numeric, errors='coerce').dropna()
    return df

def get_daily_trend(df_1d):
    # Use June 5 and June 6 for this example
    if "2025-06-05" not in df_1d.index.strftime("%Y-%m-%d") or "2025-06-06" not in df_1d.index.strftime("%Y-%m-%d"):
        return "❌ Required dates not found in 1D data."

    df_1d = df_1d.copy()
    df_1d['EMA_9'] = EMAIndicator(close=df_1d['Close'], window=9).ema_indicator()
    df_1d['EMA_21'] = EMAIndicator(close=df_1d['Close'], window=21).ema_indicator()
    vwap = VolumeWeightedAveragePrice(
        high=df_1d['High'], low=df_1d['Low'], close=df_1d['Close'], volume=df_1d['Volume']
    )
    df_1d['VWAP'] = vwap.volume_weighted_average_price()

    day_before = df_1d.loc["2025-06-05"]
    today = df_1d.loc["2025-06-06"]

    if today["Open"] > day_before["High"] and today["Open"] > today["EMA_9"] and today["Open"] > today["EMA_21"] and today["Open"] > today["VWAP"]:
        return "📈 Bullish daily trend (opened above yesterday's high and all MAs)"
    elif today["Open"] < day_before["Low"] and today["Open"] < today["EMA_9"] and today["Open"] < today["EMA_21"] and today["Open"] < today["VWAP"]:
        return "📉 Bearish daily trend (opened below yesterday's low and all MAs)"
    else:
        return "🔄 Mixed or neutral daily open"

def get_hourly_trend(df_1h):
    df_1h = df_1h.copy()
    df_1h['EMA_9'] = EMAIndicator(close=df_1h['Close'], window=9).ema_indicator()
    df_1h['EMA_21'] = EMAIndicator(close=df_1h['Close'], window=21).ema_indicator()
    vwap = VolumeWeightedAveragePrice(
        high=df_1h['High'], low=df_1h['Low'], close=df_1h['Close'], volume=df_1h['Volume']
    )
    df_1h['VWAP'] = vwap.volume_weighted_average_price()

    candle_1030 = df_1h.between_time("10:30", "10:30").loc["2025-06-06"]
    if candle_1030.empty:
        return "❌ No 10:30 AM candle data available."

    row = candle_1030.iloc[-1]
    condition = []

    if row['Close'] > row['EMA_9']: condition.append("above EMA 9")
    if row['Close'] > row['EMA_21']: condition.append("above EMA 21")
    if row['Close'] > row['VWAP']: condition.append("above VWAP")

    if len(condition) >= 2:
        return f"✅ 10:30 candle closed strong: {', '.join(condition)}"
    else:
        return f"⚠️ 10:30 candle shows weakness: {', '.join(condition)}"

def get_fib_retrace_status(df_15m):
    df_15m = df_15m.copy()
    recent = df_15m.between_time("09:30", "11:30").loc["2025-06-06"]
    if recent.empty or len(recent) < 2:
        return "❌ Not enough 15M candles between 9:30–11:30 on June 6."

    high = recent['High'].max()
    low = recent['Low'].min()
    last_price = recent.iloc[-1]['Close']
    retrace_level_50 = high - 0.5 * (high - low)
    retrace_level_61 = high - 0.618 * (high - low)

    if retrace_level_61 <= last_price <= retrace_level_50:
        return f"🔁 Retracement zone: {last_price:.2f} is in 50–61.8% zone"
    elif last_price > high:
        return f"🚀 Breaking high: {last_price:.2f} above 9:30–11:30 high"
    elif last_price < low:
        return f"📉 Breaking low: {last_price:.2f} below 9:30–11:30 low"
    else:
        return f"🔍 Price: {last_price:.2f} outside fib zone"

