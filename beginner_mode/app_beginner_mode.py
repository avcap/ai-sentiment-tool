from beginner_mode.data_utils_beginner import load_data, calculate_indicators
from beginner_mode.chart_utils_beginner import plot_candlestick

import pandas as pd
import streamlit as st
from ta.trend import EMAIndicator
from ta.volume import VolumeWeightedAveragePrice
import mplfinance as mpf
import matplotlib.pyplot as plt

# === CONFIG ===
DATA_DIR = "data/fixed"
TICKER = "SPY"

# === UTILITY FUNCTIONS ===
def find_last_range_day_open(daily_df, today_open, current_date):
    dates = sorted(set(daily_df.index.date))
    try:
        current_idx = dates.index(current_date)
    except ValueError:
        return None, None, None  # If date not found in daily_df

    for i in range(current_idx - 1, -1, -1):
        prev_day_df = daily_df[daily_df.index.date == dates[i]]
        if not prev_day_df.empty:
            prev = prev_day_df.iloc[0]
            if prev["Low"] <= today_open <= prev["High"]:
                return prev["High"], prev["Low"], prev.name.date()
    return None, None, None

def determine_trend(df):
    last = df.iloc[-1]
    if pd.isna(last["EMA9"]) or pd.isna(last["EMA21"]) or pd.isna(last["VWAP"]):
        return "Insufficient data"
    if last["Close"] > last["EMA9"] > last["EMA21"] > last["VWAP"]:
        return "Uptrend"
    elif last["Close"] < last["EMA9"] < last["EMA21"] < last["VWAP"]:
        return "Downtrend"
    else:
        return "Sideways / Undecided"

# === STREAMLIT APP ===
st.set_page_config(layout="wide", page_title="Beginner Mode - SPY Analysis")
st.title(f"📈 Beginner Mode: {TICKER} Analysis")

# Load CSVs
daily_df = load_data(f"{DATA_DIR}/{TICKER}_1d.csv")
hourly_df = load_data(f"{DATA_DIR}/{TICKER}_1h.csv")
min15_df = load_data(f"{DATA_DIR}/{TICKER}_15m.csv")

# === Date Selection ===
available_dates = sorted(set(min15_df.index.date), reverse=True)
selected_date = st.selectbox("Select Trading Day for Analysis", available_dates)
selected_open_row = min15_df[min15_df.index.date == selected_date]

if selected_open_row.empty:
    st.error("No 15-minute data for the selected date.")
    st.stop()

today_open = selected_open_row.iloc[0]["Open"]
current_date = selected_open_row.index[0].date()

# === Step 1: Daily Range Check ===
high, low, ref_date = find_last_range_day_open(daily_df, today_open, current_date)

if high is not None:
    st.subheader("📊 1D Range Analysis")
    st.markdown(f"- 📅 **Reference Day:** `{ref_date}`")
    st.markdown(f"- 🔼 **Resistance (High):** `{high:.2f}`")
    st.markdown(f"- 🔽 **Support (Low):** `{low:.2f}`")
    st.markdown(f"- 📌 **Today's Open:** `{today_open:.2f}`")
else:
    st.error("❗ Today's open is outside the high/low of recent daily candles. Could indicate breakout.")

# === Step 2: 1H Trend Confirmation ===
hourly_df = calculate_indicators(hourly_df)
last_hour = hourly_df.loc[hourly_df.index.date == current_date]
if not last_hour.empty:
    last_hour = last_hour.iloc[-1]
    trend = determine_trend(hourly_df)

    st.subheader("⏰ 1H Trend Confirmation")
    st.markdown(f"""
    - **Close:** `{last_hour['Close']:.2f}`  
    - **EMA 9:** `{last_hour['EMA9']:.2f}`  
    - **EMA 21:** `{last_hour['EMA21']:.2f}`  
    - **VWAP:** `{last_hour['VWAP']:.2f}`  
    - **Trend Bias:** `{trend}`
    """)
else:
    st.warning("⚠️ No hourly data found for selected day.")

# === Step 3: 15-Minute Candlestick Chart ===
st.subheader("🕒 15-Minute Chart View")
plot_candlestick(min15_df[min15_df.index.date == selected_date], title=f"{TICKER} 15-Min Chart — {selected_date}")

