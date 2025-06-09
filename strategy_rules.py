def analyze_with_zones(df, zones=None):
    signals = []

    if zones is None:
        zones = []

    zone_index_price_map = {(idx, z_type): df.loc[idx, 'Close'] for idx, z_type in zones if idx in df.index}

    for i in range(2, len(df)):
        idx = df.index[i]
        current_close = df['Close'].iloc[i]
        prev_close = df['Close'].iloc[i - 1]
        prev_open = df['Open'].iloc[i - 1]
        prev_prev_close = df['Close'].iloc[i - 2]

        body = abs(df['Close'].iloc[i] - df['Open'].iloc[i])
        range_ = df['High'].iloc[i] - df['Low'].iloc[i]
        upper_shadow = df['High'].iloc[i] - max(df['Close'].iloc[i], df['Open'].iloc[i])
        lower_shadow = min(df['Close'].iloc[i], df['Open'].iloc[i]) - df['Low'].iloc[i]

        # Detect common patterns
        if body < range_ * 0.3 and upper_shadow > body and lower_shadow > body:
            pattern = 'doji'
        elif df['Close'].iloc[i] > df['Open'].iloc[i] and df['Close'].iloc[i] > prev_close:
            pattern = 'bullish_engulfing'
        elif df['Close'].iloc[i] < df['Open'].iloc[i] and df['Close'].iloc[i] < prev_close:
            pattern = 'bearish_engulfing'
        else:
            pattern = None

        # Add signal only if it aligns with zone
        for (z_idx, z_type), z_price in zone_index_price_map.items():
            if abs(df.loc[idx, 'Close'] - z_price) / z_price < 0.002:  # within 0.2%
                if pattern:
                    signals.append((idx, pattern, z_type))

    return signals
