import pandas as pd

def detect_zones(df, lookback=20):
    supports = []
    resistances = []

    for i in range(lookback, len(df) - lookback):
        low = df['Low'].iloc[i]
        high = df['High'].iloc[i]
        prev_lows = df['Low'].iloc[i - lookback:i]
        next_lows = df['Low'].iloc[i + 1:i + 1 + lookback]
        prev_highs = df['High'].iloc[i - lookback:i]
        next_highs = df['High'].iloc[i + 1:i + 1 + lookback]

        if low <= prev_lows.min() and low <= next_lows.min():
            supports.append((df.index[i], low))

        if high >= prev_highs.max() and high >= next_highs.max():
            resistances.append((df.index[i], high))

    zone_points = [(idx, 'support') for idx, _ in supports] + [(idx, 'resistance') for idx, _ in resistances]
    return zone_points
