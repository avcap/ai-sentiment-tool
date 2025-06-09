import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import plotly.graph_objects as go

# Add parent directory to sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from strategy_rules import analyze_with_zones
from zone_detection import detect_zones

st.set_page_config(layout="centered", page_title="Beginner Mode Analysis", page_icon="📈")

DATA_DIR = "/Users/acap/ai-sentiment-tool/data/fixed"

@st.cache_data
def load_data(ticker):
    df_1d = pd.read_csv(os.path.join(DATA_DIR, f"{ticker}_1d.csv"), index_col=0, parse_dates=True)
    df_1h = pd.read_csv(os.path.join(DATA_DIR, f"{ticker}_1h.csv"), index_col=0, parse_dates=True)
    df_15m = pd.read_csv(os.path.join(DATA_DIR, f"{ticker}_15m.csv"), index_col=0, parse_dates=True)

    df_1d.index = df_1d.index.tz_localize('UTC').tz_convert('US/Eastern')
    df_1h.index = df_1h.index.tz_localize('UTC').tz_convert('US/Eastern')
    df_15m.index = df_15m.index.tz_localize('UTC').tz_convert('US/Eastern')

    return df_1d, df_1h, df_15m

ticker = "SPY"
df_1d, df_1h, df_15m = load_data(ticker)

available_dates = sorted(list(set(df_15m.index.date)), reverse=True)
selected_date = st.selectbox("Select a trading date:", available_dates)

# Filter for the last 5 trading days from selected date
selected_datetime = datetime.combine(selected_date, datetime.min.time())
last_5_dates = sorted([d for d in set(df_15m.index.date) if d <= selected_date], reverse=True)[:5]

# Safe DataFrame filtering
df_1h_filtered = df_1h[pd.Series(df_1h.index.date, index=df_1h.index).isin(last_5_dates)].copy()
df_15m_filtered = df_15m[pd.Series(df_15m.index.date, index=df_15m.index).isin(last_5_dates)].copy()

# Detect strategy signals and zones
zones_1h = detect_zones(df_1h_filtered)
zones_15m = detect_zones(df_15m_filtered)
signals_1h = analyze_with_zones(df_1h_filtered)
signals_15m = analyze_with_zones(df_15m_filtered)

# Filter to show only confluence signals (at zones)
def filter_signals_at_zones(signals, zones):
    zone_indices = set([z[0] for z in zones if len(z) >= 1])
    return [(idx, signal, z_type) for idx, signal, z_type in signals if idx in zone_indices]

signals_1h = filter_signals_at_zones(signals_1h, zones_1h)
signals_15m = filter_signals_at_zones(signals_15m, zones_15m)

# Plotting function
def plot_chart(df, title, signals, zones):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        increasing_line_color='darkgreen',
        decreasing_line_color='darkred',
        name='Candles'
    ))

    df.loc[:, 'EMA_9'] = df['Close'].ewm(span=9).mean()
    df.loc[:, 'EMA_21'] = df['Close'].ewm(span=21).mean()
    df.loc[:, 'VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()

    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], mode='lines', name='EMA 9', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], mode='lines', name='EMA 21', line=dict(color='cyan')))
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], mode='lines', name='VWAP', line=dict(color='purple', dash='dot')))

    for z in zones:
        if len(z) == 2:
            idx, zone_type = z
        elif len(z) == 3:
            idx, zone_type, _ = z
        else:
            continue

        zone_color = 'blue' if zone_type == 'support' else 'orange'
        if idx in df.index:
            zone_price = df.loc[idx, 'Close']
            fig.add_hline(y=zone_price, line_dash="dash", line_color=zone_color,
                          annotation_text=f"{zone_type.title()} Zone",
                          annotation_position="top left")

    for idx, signal, zone_type in signals:
        if idx in df.index:
            color = 'green' if 'bullish' in signal else 'red'
            fig.add_trace(go.Scatter(
                x=[idx], y=[df.loc[idx, 'Close']],
                mode='markers', name=signal,
                marker=dict(color=color, size=12, symbol='circle')
            ))

    fig.update_layout(title=title,
                      xaxis_title='Time',
                      yaxis_title='Price',
                      xaxis_rangeslider_visible=False,
                      plot_bgcolor='white',
                      paper_bgcolor='grey',
                      font=dict(color='black'),
                      hoverlabel=dict(bgcolor='black', font_color='white'),
                      xaxis=dict(showgrid=True, color='grey', tickfont=dict(color='grey'), titlefont=dict(color='black')),
                      yaxis=dict(showgrid=True, color='grey', tickfont=dict(color='grey'), titlefont=dict(color='black')))

    st.plotly_chart(fig, use_container_width=True)

# Display layout
st.markdown("## 📉 Beginner Mode: Market Analysis")
plot_chart(df_1h_filtered, "1H Chart", signals_1h, zones_1h)
plot_chart(df_15m_filtered, "15M Chart", signals_15m, zones_15m)
