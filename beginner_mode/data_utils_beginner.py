import pandas as pd
from ta.trend import EMAIndicator
from ta.volume import VolumeWeightedAveragePrice

def load_data(path):
    df = pd.read_csv(path)
    df.columns = ["Datetime", "Close", "High", "Low", "Open", "Volume"]
    df["Datetime"] = pd.to_datetime(df["Datetime"])
    df.set_index("Datetime", inplace=True)
    df.sort_index(inplace=True)
    return df

def calculate_indicators(df):
    df = df.copy()
    if len(df) >= 21:
        df['EMA9'] = EMAIndicator(close=df['Close'], window=9).ema_indicator()
        df['EMA21'] = EMAIndicator(close=df['Close'], window=21).ema_indicator()
    elif len(df) >= 9:
        df['EMA9'] = EMAIndicator(close=df['Close'], window=9).ema_indicator()
        df['EMA21'] = None
    else:
        df['EMA9'] = None
        df['EMA21'] = None

    if len(df) > 0:
        vwap = VolumeWeightedAveragePrice(
            high=df["High"], low=df["Low"], close=df["Close"], volume=df["Volume"]
        )
        df["VWAP"] = vwap.volume_weighted_average_price()
    else:
        df["VWAP"] = None

    return df

