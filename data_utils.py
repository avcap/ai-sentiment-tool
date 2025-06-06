# data_utils.py

import yfinance as yf
import pandas as pd
import ta  # For technical analysis

def get_price_data(ticker, interval, start, end):
    try:
        df = yf.download(ticker, start=start, end=end, interval=interval)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        print("Data fetch error:", e)
        return None

def generate_technical_summary(df):
    # Example: Adding EMAs and VWAP
    df['EMA_9'] = df['Close'].ewm(span=9).mean()
    df['EMA_21'] = df['Close'].ewm(span=21).mean()

    # VWAP (using ta library)
    vwap = ta.volume.VolumeWeightedAveragePrice(
        high=df['High'], low=df['Low'], close=df['Close'], volume=df['Volume']
    )
    df['VWAP'] = vwap.vwap

    # Basic summary
    last_row = df.iloc[-1]
    summary = f"""
    Price: {last_row['Close']:.2f}
    EMA 9: {last_row['EMA_9']:.2f}
    EMA 21: {last_row['EMA_21']:.2f}
    VWAP: {last_row['VWAP']:.2f}
    Trend: {"Bullish" if last_row['EMA_9'] > last_row['EMA_21'] else "Bearish"}
    """

    return summary.strip()

