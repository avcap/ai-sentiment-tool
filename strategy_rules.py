import pandas as pd
import numpy as np
from zone_detection import detect_zones

def is_bullish_engulfing(df, i):
    return (
        df['Open'].iloc[i] < df['Close'].iloc[i] and
        df['Open'].iloc[i - 1] > df['Close'].iloc[i - 1] and
        df['Open'].iloc[i] <= df['Close'].iloc[i - 1] and
        df['Close'].iloc[i] >= df['Open'].iloc[i - 1]
    )

def is_bearish_engulfing(df, i):
    return (
        df['Open'].iloc[i] > df['Close'].iloc[i] and
        df['Open'].iloc[i - 1] < df['Close'].iloc[i - 1] and
        df['Open'].iloc[i] >= df['Close'].iloc[i - 1] and
        df['Close'].iloc[i] <= df['Open'].iloc[i - 1]
    )

def is_doji(df, i, threshold=0.2):
    body = abs(df['Close'].iloc[i] - df['Open'].iloc[i])
    high_low = df['High'].iloc[i] - df['Low'].iloc[i]
    return high_low > 0 and (body / high_low) < threshold

def is_pin_bar(df, i, body_ratio=0.3, wick_ratio=2):
    body = abs(df['Close'].iloc[i] - df['Open'].iloc[i])
    upper_wick = df['High'].iloc[i] - max(df['Close'].iloc[i], df['Open'].iloc[i])
    lower_wick = min(df['Close'].iloc[i], df['Open'].iloc[i]) - df['Low'].iloc[i]
    total_range = body + upper_wick + lower_wick
    if total_range == 0 or pd.isna(total_range):
        return False
    return (body / total_range) < body_ratio and (
        upper_wick > wick_ratio * body or lower_wick > wick_ratio * body
    )

def is_inside_bar(df, i):
    return (
        df['High'].iloc[i] < df['High'].iloc[i - 1] and
        df['Low'].iloc[i] > df['Low'].iloc[i - 1]
    )

def analyze_with_zones(df, zone_score_threshold=2):
    zones = detect_zones(df)
    signals = []

    # Fix zone unpacking to match zone format
    zone_map = {(idx, z_type): (price, score) for idx, z_type, price, score in zones}

    for i in range(1, len(df)):
        idx = df.index[i]

        if is_bullish_engulfing(df, i):
            signal = 'bullish_engulfing'
        elif is_bearish_engulfing(df, i):
            signal = 'bearish_engulfing'
        elif is_doji(df, i):
            signal = 'doji'
        elif is_pin_bar(df, i):
            signal = 'pin_bar'
        elif is_inside_bar(df, i):
            signal = 'inside_bar'
        else:
            continue

        # Match signal index with zone index and score
        for (zone_idx, z_type), (price, score) in zone_map.items():
            if idx == zone_idx and score >= zone_score_threshold:
                signals.append((idx, signal, z_type, score))
                break

    return signals
