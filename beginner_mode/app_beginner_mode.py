import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
import pytz
import plotly.graph_objects as go

# Extend system path for module import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from strategy_rules import analyze_with_zones
from zone_detection import detect_zones, simplify_zones

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

# Date selector
available_dates = sorted(list(set(df_15m.index.date)), reverse=True)
selected_date = st.selectbox("Select a trading date:", available_dates)
last_5_dates = sorted([d for d in set(df_15m.index.date) if d <= selected_date], reverse=True)[:5]

# Filter data
df_1h_filtered = df_1h[pd.Series(df_1h.index.date, index=df_1h.index).isin(last_5_dates)].copy()
df_15m_filtered = df_15m[pd.Series(df_15m.index.date, index=df_15m.index).isin(last_5_dates)].copy()

# Detect zones + signals
zones_1h_full = detect_zones(df_1h_filtered)
zones_15m_full = detect_zones(df_15m_filtered)

zones_1h = simplify_zones(zones_1h_full, df_1h_filtered, window=0.035)
zones_15m = simplify_zones(zones_15m_full, df_15m_filtered)

signals_1h = analyze_with_zones(df_1h_filtered)
signals_15m = analyze_with_zones(df_15m_filtered)

def plot_chart(df, title, signals, zones):
    fig = go.Figure()

    # Indicators
    df['EMA_9'] = df['Close'].ewm(span=9).mean()
    df['EMA_21'] = df['Close'].ewm(span=21).mean()
    df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='green',
        decreasing_line_color='darkred',
        name='Candles'
    ))

    # EMAs and VWAP
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], mode='lines', name='EMA 9', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], mode='lines', name='EMA 21', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], mode='lines', name='VWAP', line=dict(color='purple', dash='dot')))

    # Zones
    for idx, z_type, price, score in zones:
        if score < 2:
            continue
        color = 'blue' if z_type == 'support' else 'orange'
        fig.add_hline(y=price, line_dash='dash', line_color=color,
                      annotation_text=f"{z_type.title()} Zone (score {score})",
                      annotation_position='top right')

    # Signals at high-score zones
    for idx, signal, z_type, score in signals:
        if idx in df.index and score >= 2:
            color = 'green' if 'bullish' in signal else 'red'
            fig.add_trace(go.Scatter(
                x=[idx], y=[df.loc[idx, 'Close']],
                mode='markers',
                marker=dict(size=10, color=color, symbol='circle'),
                name=signal
            ))

    fig.update_layout(
        title=title,
        xaxis_title='Time',
        yaxis_title='Price',
        plot_bgcolor='white',
        paper_bgcolor='grey',
        font=dict(color='black'),
        hoverlabel=dict(bgcolor='black', font_color='white'),
        xaxis=dict(showgrid=True, tickfont=dict(color='grey')),
        yaxis=dict(showgrid=True, tickfont=dict(color='grey')),
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)

# Display
st.markdown("## 📉 Beginner Mode: Market Analysis")
plot_chart(df_1h_filtered, "1H Chart", signals_1h, zones_1h)
plot_chart(df_15m_filtered, "15M Chart", signals_15m, zones_15m)
