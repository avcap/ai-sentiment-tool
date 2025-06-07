import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
import pandas as pd

def plot_candlestick(df, title="Candlestick Chart"):
    if df.empty:
        st.warning("⚠️ No data available for chart.")
        return

    fig, ax = plt.subplots(figsize=(10, 5))

    df = df.copy()
    df['Color'] = ['green' if close >= open_ else 'red' for open_, close in zip(df['Open'], df['Close'])]

    for idx, row in df.iterrows():
        ax.plot([idx, idx], [row['Low'], row['High']], color='black', linewidth=1)
        ax.add_patch(plt.Rectangle(
            (mdates.date2num(idx) - 0.2, min(row['Open'], row['Close'])),
            0.4,
            abs(row['Open'] - row['Close']),
            color=row['Color']
        ))

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%b %d'))
    ax.set_title(title)
    ax.set_ylabel("Price")
    ax.grid(True)
    st.pyplot(fig)

