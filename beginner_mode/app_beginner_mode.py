import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, time

# Load and preprocess data
@st.cache_data
def load_and_prepare_data():
    def load_csv(file):
        df = pd.read_csv(file)
        df.columns = [col.strip() for col in df.columns]
        df['Datetime'] = pd.to_datetime(df.iloc[:, 0], utc=True).dt.tz_convert("America/New_York")
        df.set_index('Datetime', inplace=True)
        return df

    df_1d = pd.read_csv("data/fixed/SPY_1d.csv")
    df_1d.columns = [col.strip() for col in df_1d.columns]
    df_1d['Date'] = pd.to_datetime(df_1d.iloc[:, 0]).dt.date

    df_1h = load_csv("data/fixed/SPY_1h.csv")
    df_15m = load_csv("data/fixed/SPY_15m.csv")

    return df_1d, df_1h, df_15m

# Load the data
df_1d, df_1h, df_15m = load_and_prepare_data()

# Selectable date from user input
available_dates = sorted(list(set(df_1h.index.date) & set(df_15m.index.date)))
selected_date = st.selectbox("📅 Select Date", sorted(available_dates, reverse=True), index=0)

# Define market session window
session_start = time(9, 30)
session_end = time(11, 30)

# Get last 5 trading days including and before selected date
last_5_dates = [d for d in available_dates if d <= selected_date][-5:]

# Get today's open from 1D CSV
daily_row = df_1d[df_1d['Date'] == selected_date]
open_today = None
if not daily_row.empty:
    open_today = daily_row.iloc[0]['Open']

resistance, support = None, None
res_day, sup_day = None, None
if open_today:
    prior_days = df_1d[df_1d['Date'] < selected_date]
    res_row = prior_days[prior_days['High'] > open_today].tail(1)
    if not res_row.empty:
        resistance = res_row['High'].values[0]
        res_day = res_row['Date'].values[0]

    sup_row = prior_days[prior_days['Low'] < open_today].tail(1)
    if not sup_row.empty:
        support = sup_row['Low'].values[0]
        sup_day = sup_row['Date'].values[0]

st.subheader("\U0001F4CA 1D Support & Resistance Analysis")
st.markdown(f"**Resistance:** `{resistance:.2f}` *(from {res_day})*" if resistance else "`No resistance found`")
st.markdown(f"**Support:** `{support:.2f}` *(from {sup_day})*" if support else "`No support found`")
st.markdown(f"**Today's Open (first candle after 9:30 AM):** `{open_today:.2f}`" if open_today else "`No valid open found`")

st.subheader("\U0001F552 1H Key Candle Snapshots")
hourly_today = df_1h[df_1h.index.date == selected_date]
snapshot_window = hourly_today[(hourly_today.index.time >= session_start) & (hourly_today.index.time <= session_end)]

if snapshot_window.empty:
    st.info("No candles between 09:30 and 11:30 for this day.")
else:
    st.dataframe(snapshot_window[['Open', 'High', 'Low', 'Close', 'Volume']])

def plot_chart(df, title):
    fig, ax = plt.subplots(figsize=(10, 3))
    mask = pd.Series(df.index.date, index=df.index).isin(last_5_dates)
    filtered = df[mask & (df.index.time >= session_start) & (df.index.time <= session_end)].copy()

    if filtered.empty:
        st.warning(f"No {title} data between 09:30–11:30 AM for selected 5-day window.")
        return

    filtered['EMA 9'] = filtered['Close'].ewm(span=9).mean()
    filtered['EMA 21'] = filtered['Close'].ewm(span=21).mean()
    filtered['VWAP'] = (filtered['Close'] * filtered['Volume']).cumsum() / filtered['Volume'].cumsum()

    ax.plot(filtered.index, filtered['EMA 9'], label='EMA 9', linewidth=1)
    ax.plot(filtered.index, filtered['EMA 21'], label='EMA 21', linewidth=1)
    ax.plot(filtered.index, filtered['VWAP'], label='VWAP', linestyle='--', linewidth=1)

    for idx, row in filtered.iterrows():
        color = 'green' if row['Close'] > row['Open'] else 'red'
        ax.vlines(x=idx, ymin=row['Low'], ymax=row['High'], color=color, linewidth=1)
        if row['Open'] == row['Close']:
            ax.scatter(idx, row['Open'], color=color, s=20)
        else:
            ax.vlines(x=idx, ymin=row['Open'], ymax=row['Close'], color=color, linewidth=4)

    if support:
        ax.axhline(support, linestyle='--', color='blue', label=f'Support ({sup_day})')
    if resistance:
        ax.axhline(resistance, linestyle='--', color='orange', label=f'Resistance ({res_day})')

    ax.set_title(f"{title} (Last 5 Days ending {selected_date}, 09:30–11:30)")
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M', tz=filtered.index.tz))
    plt.xticks(rotation=45)
    st.pyplot(fig)

st.subheader("\U0001F4C8 1H Chart")
plot_chart(df_1h, "1H Candles")

st.subheader("\U0001F553 15-Minute Chart")
plot_chart(df_15m, "15-Minute Candles")
