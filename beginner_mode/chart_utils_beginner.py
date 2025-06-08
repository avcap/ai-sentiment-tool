import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
import pandas as pd

def plot_candlestick_with_indicators(
    df, ema9=None, ema21=None, vwap=None,
    support=None, resistance=None, title="Chart", height=4, width=8,
):
    fig, ax = plt.subplots(figsize=(width, height))
    df = df.copy()
    df['Color'] = ['green' if close >= open_ else 'red'
                   for open_, close in zip(df['Open'], df['Close'])]

    # Candlesticks
    for idx, row in df.iterrows():
        ax.plot([idx, idx], [row['Low'], row['High']], color='black', linewidth=1)
        ax.add_patch(
            plt.Rectangle(
                (mdates.date2num(idx) - 0.13, min(row['Open'], row['Close'])),
                0.26,
                abs(row['Open'] - row['Close']),
                color=row['Color'],
                alpha=0.7
            )
        )

    # Indicators
    if ema9 is not None:
        ax.plot(df.index, ema9, label="EMA 9", linewidth=1.2)
    if ema21 is not None:
        ax.plot(df.index, ema21, label="EMA 21", linewidth=1.2)
    if vwap is not None:
        ax.plot(df.index, vwap, label="VWAP", linewidth=1.2, linestyle="--")

    # Support/Resistance
    if support is not None:
        ax.axhline(support, color="deepskyblue", linestyle="--", label="Support")
    if resistance is not None:
        ax.axhline(resistance, color="orange", linestyle="--", label="Resistance")

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)

