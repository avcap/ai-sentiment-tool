import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time

st.set_page_config(
    page_title="Beginner Mode App",
    layout="wide",
    initial_sidebar_state="auto"
)

# Dark Theme for Main Page with centered content
st.markdown("""
    <style>
    .main, .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 900px;
        margin: auto;
    }
    .st-bw {
        background-color: #1c1e26 !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_prepare_data():
    def load_csv(file):
        df = pd.read_csv(file)
        df.columns = [col.strip() for col in df.columns]
        df['Datetime'] = pd.to_datetime(df.iloc[:, 0], utc=True).dt.tz_convert("America/New_York")
        df.set_index('Datetime', inplace=True)
        return df

    df_1d = pd.read_csv("data/fixed/SPY_1d.csv")
    df_1d.columns = [col.strip() for col in df_1d.columns]
    df_1d['Date'] = pd.to_datetime(df_1d.iloc[:, 0]).dt.date

    df_1h = load_csv("data/fixed/SPY_1h.csv")
    df_15m = load_csv("data/fixed/SPY_15m.csv")

    return df_1d, df_1h, df_15m

df_1d, df_1h, df_15m = load_and_prepare_data()

available_dates = sorted(list(set(df_1h.index.date) & set(df_15m.index.date)), reverse=True)
selected_date = st.selectbox("📅 Select Date", available_dates, index=0)

session_start = time(9, 30)
session_end = time(11, 30)

last_5_dates = [d for d in available_dates if d <= selected_date][:5][::-1]

daily_row = df_1d[df_1d['Date'] == selected_date]
open_today = None
if not daily_row.empty:
    open_today = daily_row.iloc[0]['Open']

resistance, support = None, None
res_day, sup_day = None, None
if open_today:
    prior_days = df_1d[df_1d['Date'] < selected_date]
    res_row = prior_days[prior_days['High'] > open_today].tail(1)
    if not res_row.empty:
        resistance = res_row['High'].values[0]
        res_day = res_row['Date'].values[0]

    sup_row = prior_days[prior_days['Low'] < open_today].tail(1)
    if not sup_row.empty:
        support = sup_row['Low'].values[0]
        sup_day = sup_row['Date'].values[0]

st.subheader("📈 1D Support & Resistance Analysis")
st.markdown(f"**Resistance:** `{resistance:.2f}` *(from {res_day})*" if resistance else "`No resistance found`")
st.markdown(f"**Support:** `{support:.2f}` *(from {sup_day})*" if support else "`No support found`")
st.markdown(f"**Today's Open (from 1D CSV):** `{open_today:.2f}`" if open_today else "`No valid open found`")

st.subheader("🕐 1H Key Candle Snapshots")
hourly_today = df_1h[df_1h.index.date == selected_date]
snapshot_window = hourly_today.between_time("09:30", "11:30")

if snapshot_window.empty:
    st.info("No candles between 09:30 and 11:30 for this day.")
else:
    st.dataframe(snapshot_window[['Open', 'High', 'Low', 'Close', 'Volume']])

def plot_interactive_chart(df, title, show_ema=True, show_vwap=True):
    mask = pd.Series(df.index.date, index=df.index).isin(last_5_dates)
    filtered = df[mask].copy()
    filtered['EMA 9'] = filtered['Close'].ewm(span=9).mean()
    filtered['EMA 21'] = filtered['Close'].ewm(span=21).mean()
    filtered['VWAP'] = (filtered['Close'] * filtered['Volume']).cumsum() / filtered['Volume'].cumsum()

    if filtered.empty:
        st.warning(f"No {title} data found for last 5 trading days.")
        return

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=filtered.index,
        open=filtered['Open'],
        high=filtered['High'],
        low=filtered['Low'],
        close=filtered['Close'],
        increasing_line_color='green',
        decreasing_line_color='red',
        name='Price',
        line=dict(width=2),
        whiskerwidth=0.2
    ))

    if show_ema:
        fig.add_trace(go.Scatter(x=filtered.index, y=filtered['EMA 9'], mode='lines', name='EMA 9', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=filtered.index, y=filtered['EMA 21'], mode='lines', name='EMA 21', line=dict(color='purple')))

    if show_vwap:
        fig.add_trace(go.Scatter(x=filtered.index, y=filtered['VWAP'], mode='lines', name='VWAP', line=dict(color='orange', dash='dot')))

    if support:
        fig.add_hline(y=support, line_dash="dash", line_color="blue", annotation_text=f"Support ({sup_day})")
    if resistance:
        fig.add_hline(y=resistance, line_dash="dash", line_color="orange", annotation_text=f"Resistance ({res_day})")

    fig.update_layout(
        template='plotly_white',
        height=600,
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis_rangeslider_visible=False,
        xaxis=dict(
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            showline=True,
            showgrid=True,
            gridcolor='lightgray',
            tickfont=dict(size=12, color='black')
        ),
        yaxis=dict(
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            showline=True,
            showgrid=True,
            gridcolor='lightgray',
            tickfont=dict(size=12, color='black')
        ),
        font=dict(color='black'),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("### 1H Chart")
show_ema = st.checkbox("Show EMA", value=True, key="ema_1h")
show_vwap = st.checkbox("Show VWAP", value=True, key="vwap_1h")
plot_interactive_chart(df_1h, "1H Candles", show_ema, show_vwap)

st.markdown("### 15-Minute Chart")
show_ema_15 = st.checkbox("Show EMA", value=True, key="ema_15m")
show_vwap_15 = st.checkbox("Show VWAP", value=True, key="vwap_15m")
plot_interactive_chart(df_15m, "15-Minute Candles", show_ema_15, show_vwap_15)
