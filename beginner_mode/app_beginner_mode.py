import streamlit as st
import pandas as pd
from ta.trend import EMAIndicator
from ta.volume import VolumeWeightedAveragePrice
from datetime import datetime
import pytz
import os

# Set file paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "fixed")

daily_path = os.path.join(DATA_DIR, "SPY_1d.csv")
hourly_path = os.path.join(DATA_DIR, "SPY_1h.csv")
min15_path = os.path.join(DATA_DIR, "SPY_15m.csv")

# Load and clean CSV
def load_and_prepare(path):
    df = pd.read_csv(path)
    df.columns = ['Datetime', 'Close', 'High', 'Low', 'Open', 'Volume']  # force consistent naming
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)
    df.sort_index(inplace=True)
    return df

daily_df = load_and_prepare(daily_path)
hourly_df = load_and_prepare(hourly_path)
min15_df = load_and_prepare(min15_path)

st.title("Beginner Mode: SPY Sentiment Analysis")

# ====== DAILY ANALYSIS (Yesterday High/Low) ======
yesterday = daily_df.index[-2]
today = daily_df.index[-1]

yesterday_high = daily_df.loc[yesterday]['High']
yesterday_low = daily_df.loc[yesterday]['Low']
today_open = daily_df.loc[today]['Open']

# Calculate EMAs and VWAP
ema9 = EMAIndicator(close=daily_df['Close'], window=9).ema_indicator().iloc[-1]
ema21 = EMAIndicator(close=daily_df['Close'], window=21).ema_indicator().iloc[-1]
vwap = VolumeWeightedAveragePrice(high=daily_df['High'], low=daily_df['Low'], close=daily_df['Close'], volume=daily_df['Volume']).volume_weighted_average_price().iloc[-1]

# Determine trend
if today_open > yesterday_high and today_open > ema9 and today_open > ema21 and today_open > vwap:
    daily_trend = "Bullish"
elif today_open < yesterday_low and today_open < ema9 and today_open < ema21 and today_open < vwap:
    daily_trend = "Bearish"
else:
    daily_trend = "Sideways / Undecided"

st.subheader("1D Trend Analysis")
st.write(f"Yesterday High: {yesterday_high:.2f}, Low: {yesterday_low:.2f}")
st.write(f"Today's Open: {today_open:.2f}")
st.write(f"EMA 9: {ema9:.2f}, EMA 21: {ema21:.2f}, VWAP: {vwap:.2f}")
st.success(f"Trend: {daily_trend}")

# ====== HOURLY ANALYSIS (Simulate 10:30 AM Eastern = 14:30 UTC) ======
eastern = pytz.timezone("US/Eastern")
target_et = eastern.localize(datetime(2025, 6, 6, 10, 30))
target_utc = target_et.astimezone(pytz.utc)

if target_utc in hourly_df.index:
    hour_candle = hourly_df.loc[target_utc]
    h_close = hour_candle["Close"]
    h_ema9 = EMAIndicator(close=hourly_df['Close'], window=9).ema_indicator().loc[target_utc]
    h_ema21 = EMAIndicator(close=hourly_df['Close'], window=21).ema_indicator().loc[target_utc]
    h_vwap = VolumeWeightedAveragePrice(high=hourly_df['High'], low=hourly_df['Low'], close=hourly_df['Close'], volume=hourly_df['Volume']).volume_weighted_average_price().loc[target_utc]

    if h_close > h_ema9 and h_close > h_ema21 and h_close > h_vwap:
        hour_trend = "Bullish Continuation"
    elif h_close < h_ema9 and h_close < h_ema21 and h_close < h_vwap:
        hour_trend = "Bearish Continuation"
    else:
        hour_trend = "Possible Reversal / Sideways"

    st.subheader("1H Trend Confirmation (10:30 AM)")
    st.write(f"Close: {h_close:.2f}, EMA 9: {h_ema9:.2f}, EMA 21: {h_ema21:.2f}, VWAP: {h_vwap:.2f}")
    st.info(f"1H Sentiment: {hour_trend}")
else:
    st.warning("10:30 AM 1H candle not found in hourly data.")

# ====== 15M ANALYSIS (Retracement or Reversal) ======
last_15m = min15_df.iloc[-1]
retracement_zone = [0.5, 0.618]
high = min15_df['High'].max()
low = min15_df['Low'].min()
pullback = last_15m["Close"]

fib_50 = high - (high - low) * retracement_zone[0]
fib_61 = high - (high - low) * retracement_zone[1]

if fib_61 <= pullback <= fib_50:
    action_advice = "Watch for Trend Continuation (Good Entry Zone)"
elif pullback < fib_61:
    action_advice = "Caution: Possible Reversal Below 61% Fib"
else:
    action_advice = "Extended Move – Wait for Pullback"

st.subheader("15M Fib Retracement Analysis")
st.write(f"Fib Zone: {fib_61:.2f} – {fib_50:.2f}, Last Close: {pullback:.2f}")
st.warning(action_advice)

# ====== Final Summary ======
st.subheader("Beginner Sentiment Summary")
st.write(f"- Daily Trend: **{daily_trend}**")
if 'hour_trend' in locals():
    st.write(f"- 1H Confirmation: **{hour_trend}**")
st.write(f"- 15M Analysis: **{action_advice}**")



