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
    df['EMA9'] = EMAIndicator(close=df['Close'], window=9).ema_indicator()
    df['EMA21'] = EMAIndicator(close=df['Close'], window=21).ema_indicator()
    if len(df) > 0:
        vwap = VolumeWeightedAveragePrice(high=df["High"], low=df["Low"], close=df["Close"], volume=df["Volume"])
        df["VWAP"] = vwap.volume_weighted_average_price()
    else:
        df["VWAP"] = None
    return df

def find_breakout_levels(daily_df, today_open, today_low):
    # If today's open > yesterday's high: find support at yest high, resistance at next higher high in past
    # If today's low < yesterday's low: find resistance at yest low, support at next lower low in past
    days = daily_df.sort_index()
    yesterday = days.iloc[-2]
    support, resistance, ref_support, ref_resistance = None, None, None, None

    # Open breakout up (gap above)
    if today_open > yesterday["High"]:
        support = yesterday["High"]
        ref_support = days.index[-2].date()
        for i in range(len(days) - 2 - 1, -1, -1):
            if days.iloc[i]["High"] > today_open:
                resistance = days.iloc[i]["High"]
                ref_resistance = days.index[i].date()
                break
        return support, ref_support, resistance, ref_resistance, "breakout_up"
    # Low breakout down (gap down)
    elif today_low < yesterday["Low"]:
        resistance = yesterday["Low"]
        ref_resistance = days.index[-2].date()
        for i in range(len(days) - 2 - 1, -1, -1):
            if days.iloc[i]["Low"] < today_open:
                support = days.iloc[i]["Low"]
                ref_support = days.index[i].date()
                break
        return support, ref_support, resistance, ref_resistance, "breakout_down"
    # Otherwise: normal in-range
    else:
        for i in range(len(days) - 2, -1, -1):
            prev = days.iloc[i]
            if prev["Low"] <= today_open <= prev["High"]:
                return prev["Low"], days.index[i].date(), prev["High"], days.index[i].date(), "inside"
        return None, None, None, None, "none"

