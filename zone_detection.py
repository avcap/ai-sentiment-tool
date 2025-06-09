import pandas as pd

def detect_zones(df, lookback=20, threshold=3):
    supports = []
    resistances = []

    for i in range(lookback, len(df) - lookback):
        low = df['Low'].iloc[i]
        high = df['High'].iloc[i]
        prev_lows = df['Low'].iloc[i - lookback:i]
        next_lows = df['Low'].iloc[i + 1:i + 1 + lookback]
        prev_highs = df['High'].iloc[i - lookback:i]
        next_highs = df['High'].iloc[i + 1:i + 1 + lookback]

        # Identify support zone
        if low <= prev_lows.min() and low <= next_lows.min():
            score = ((prev_lows <= low + threshold).sum() + (next_lows <= low + threshold).sum())
            supports.append((df.index[i], 'support', low, score))

        # Identify resistance zone
        if high >= prev_highs.max() and high >= next_highs.max():
            score = ((prev_highs >= high - threshold).sum() + (next_highs >= high - threshold).sum())
            resistances.append((df.index[i], 'resistance', high, score))

    # Combine and sort all zones
    zones = supports + resistances
    zones = sorted(zones, key=lambda x: x[3], reverse=True)  # Sort by strength
    return zones

def simplify_zones(zones, df, price_col='Close', max_zones=2, window=0.025):
    if df.empty or not zones:
        return []

    current_price = df[price_col].iloc[-1]
    filtered = []

    for z_type in ['support', 'resistance']:
        type_zones = [(idx, t, p, s) for idx, t, p, s in zones if t == z_type]
        type_zones = [z for z in type_zones if abs(z[2] - current_price) / current_price <= window]
        type_zones.sort(key=lambda x: x[3], reverse=True)
        filtered.extend(type_zones[:max_zones])

    return filtered
