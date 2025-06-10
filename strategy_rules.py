import pandas as pd
import numpy as np
from zone_detection import detect_zones


# === Candlestick Pattern Definitions ===

def is_bullish_engulfing(df, i):
    return df['Open'][i] < df['Close'][i] and df['Open'][i-1] > df['Close'][i-1] and \
           df['Open'][i] <= df['Close'][i-1] and df['Close'][i] >= df['Open'][i-1]

def is_bearish_engulfing(df, i):
    return df['Open'][i] > df['Close'][i] and df['Open'][i-1] < df['Close'][i-1] and \
           df['Open'][i] >= df['Close'][i-1] and df['Close'][i] <= df['Open'][i-1]

def is_doji(df, i, threshold=0.1):
    body = abs(df['Close'][i] - df['Open'][i])
    high_low = df['High'][i] - df['Low'][i]
    return high_low > 0 and (body / high_low) < threshold

def is_pin_bar(df, i, body_ratio=0.3, wick_ratio=2):
    body = abs(df['Close'][i] - df['Open'][i])
    upper_wick = df['High'][i] - max(df['Close'][i], df['Open'][i])
    lower_wick = min(df['Close'][i], df['Open'][i]) - df['Low'][i]
    return (body / (upper_wick + lower_wick + body)) < body_ratio and \
           (upper_wick > wick_ratio * body or lower_wick > wick_ratio * body)

def is_inside_bar(df, i):
    return df['High'][i] < df['High'][i - 1] and df['Low'][i] > df['Low'][i - 1]

def is_morning_star(df, i):
    return df['Close'][i-2] < df['Open'][i-2] and abs(df['Open'][i-1] - df['Close'][i-1]) < 0.1 * (df['High'][i-1] - df['Low'][i-1]) and \
           df['Close'][i] > df['Open'][i] and df['Close'][i] > df['Close'][i-2]

def is_evening_star(df, i):
    return df['Close'][i-2] > df['Open'][i-2] and abs(df['Open'][i-1] - df['Close'][i-1]) < 0.1 * (df['High'][i-1] - df['Low'][i-1]) and \
           df['Close'][i] < df['Open'][i] and df['Close'][i] < df['Close'][i-2]

# === Main Analysis Function ===

def analyze_with_zones(df, selected_date, zone_score_threshold=2, verbose=False):
    # Convert index to Eastern and copy to avoid SettingWithCopy
    df = df.copy()
    df.index = df.index.tz_convert('US/Eastern')

    # Ensure selected_date is a datetime.date object
    df['Date'] = df.index.date
    selected_date = pd.to_datetime(selected_date).date()

    # Split: Use prior data to detect zones
    prior_df = df[df['Date'] < selected_date]
    current_df = df[df['Date'] == selected_date].between_time("09:30", "12:00")

    # Detect zones from prior days only
    zones = detect_zones(prior_df)
    zone_map = {(idx, z_type): (price, score) for idx, z_type, price, score in zones}

    signals = []
    for i in range(2, len(current_df)):  # Start at 2 to allow for 2-candle patterns
        idx = current_df.index[i]
        if is_bullish_engulfing(current_df, i):
            signal = 'bullish_engulfing'
        elif is_bearish_engulfing(current_df, i):
            signal = 'bearish_engulfing'
        elif is_doji(current_df, i):
            signal = 'doji'
        elif is_pin_bar(current_df, i):
            signal = 'pin_bar'
        elif is_inside_bar(current_df, i):
            signal = 'inside_bar'
        else:
            continue

        # Match against known zones
        for (zone_idx, z_type), (price, score) in zone_map.items():
            if score >= zone_score_threshold and abs((idx - zone_idx).total_seconds()) <= 3600 * 2:
                if verbose:
                    print(f"[{idx.strftime('%Y-%m-%d %H:%M')}] {signal.upper()} near {z_type.upper()} (score: {score}) at price: ${current_df['Close'][i]:.2f}")
                signals.append((idx, signal, z_type, score, current_df['Close'][i]))
                break

    return signals
