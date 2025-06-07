# data_utils.py
import pandas as pd
import os
from ta.trend import EMAIndicator
from ta.volume import VolumeWeightedAveragePrice
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def get_price_data(ticker, interval, data_dir="data/fixed"):
    path = os.path.join(data_dir, f"{ticker}_{interval}.csv")
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[df.index.notna()] #optional: drop rows with invalid dates
    df.columns = [col.strip() for col in df.columns]
    df = df.apply(pd.to_numeric, errors='coerce')
    df = df.dropna()
    return df

def generate_technical_summary(df):
    df['EMA_9'] = EMAIndicator(close=df['Close'], window=9).ema_indicator()
    df['EMA_21'] = EMAIndicator(close=df['Close'], window=21).ema_indicator()
    vwap = VolumeWeightedAveragePrice(high=df['High'], low=df['Low'], close=df['Close'], volume=df['Volume'])
    df['VWAP'] = vwap.volume_weighted_average_price()

    last = df.iloc[-1]
    trend = "Bullish" if last['EMA_9'] > last['EMA_21'] else "Bearish"
    above_vwap = last['Close'] > last['VWAP']

    summary = (
        f"Current Trend: {trend}\n"
        f"Close Price: {last['Close']:.2f}\n"
        f"VWAP: {last['VWAP']:.2f} ({'Above' if above_vwap else 'Below'})\n"
        f"EMA 9: {last['EMA_9']:.2f}, EMA 21: {last['EMA_21']:.2f}"
    )
    return summary

def generate_gpt_sentiment(tech_summary):
    prompt = (
        "You are a trading assistant. Based on the technical summary provided,"
        " give a short trading sentiment (Bullish, Bearish, Neutral) and one sentence explanation.\n"
        f"Technical Summary:\n{tech_summary}"
    )
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a technical trading analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

