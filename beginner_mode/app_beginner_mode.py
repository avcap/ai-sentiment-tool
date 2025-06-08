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

# Select available dates from actual intersection of intraday charts
available_dates = sorted(list(set(df_1h.index.date) & set(df_15m.index.date)))
selected_date = st.selectbox("\U0001F4C5 Select Date", available_dates, index=len(available_dates)-1)

# Define open from first 1H candle after 9:30 AM
session_start = time(9, 00)
open_today = None
try:
    first_candle = df_1h[(df_1h.index.date == selected_date) & (df_1h.index.time >= session_start)].iloc[0]
    open_today = first_candle['Open']
except IndexError:
    pass

# Support and resistance based on prior days
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

# Display daily analysis
st.subheader("\U0001F4CA 1D Support & Resistance Analysis")
st.markdown(f"**Resistance:** `{resistance:.2f}` *(from {res_day})*" if resistance else "`No resistance found`")
st.markdown(f"**Support:** `{support:.2f}` *(from {sup_day})*" if support else "`No support found`")
st.markdown(f"**Today's Open (first 1H after 9:30 AM):** `{open_today:.2f}`" if open_today else "`No valid open found`")

# Extract 09:30 and 10:30 candles from 1H
st.subheader("\U0001F552 1H Key Candle Snapshots")
snapshot_times = [time(9, 00), time(11, 00)]
hourly_today = df_1h[df_1h.index.date == selected_date]
snapshot_candles = hourly_today[hourly_today.index.map(lambda x: x.time() in snapshot_times)]
if snapshot_candles.empty:
    st.info("No 09:30 or 10:30 candles for this day.")
else:
    st.dataframe(snapshot_candles[['Open', 'High', 'Low', 'Close', 'Volume']])

# Chart plotting function with zoom on 09:30–11:30

def plot_chart(df, title):
    fig, ax = plt.subplots(figsize=(10, 3))
    filtered = df[(df.index.date == selected_date) &
                  (df.index.time >= time(9, 00)) &
                  (df.index.time <= time(11, 00))].copy()

    if filtered.empty:
        st.warning(f"No {title} data between 09:30–11:30 AM for {selected_date}.")
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
        ax.vlines(x=idx, ymin=row['Open'], ymax=row['Close'], color=color, linewidth=4)

    if support:
        ax.axhline(support, linestyle='--', color='blue', label=f'Support ({sup_day})')
    if resistance:
        ax.axhline(resistance, linestyle='--', color='orange', label=f'Resistance ({res_day})')

    ax.set_title(f"{title} for {selected_date}")
    ax.legend()
    ax.set_xlim([pd.Timestamp(f"{selected_date} 09:00", tz=filtered.index.tz),
                 pd.Timestamp(f"{selected_date} 11:00", tz=filtered.index.tz)])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=filtered.index.tz))
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Plot 1H and 15M windows
st.subheader("\U0001F4C8 1H Chart")
plot_chart(df_1h, "1H Candles")

st.subheader("\U0001F553 15-Minute Chart")
plot_chart(df_15m, "15-Minute Candles")

