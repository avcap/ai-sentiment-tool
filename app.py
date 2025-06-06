# app.py

import streamlit as st
from data_utils import get_price_data, generate_technical_summary
from gpt_prompt import ask_gpt

st.set_page_config(page_title="AI Chart Sentiment Tool", layout="wide")
st.title("📈 AI Chart Sentiment Tool")

# Sidebar inputs
ticker = st.sidebar.text_input("Enter Ticker Symbol", value="SPY")
interval = st.sidebar.selectbox("Select Timeframe", ["1m", "5m", "15m", "1h", "1d"])
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

# Load and show chart data
if st.sidebar.button("Analyze"):
    with st.spinner("Fetching data..."):
        df = get_price_data(ticker, interval, start_date, end_date)
    
    if df is not None and not df.empty:
        st.subheader(f"{ticker} Candlestick Data")
        st.dataframe(df.tail())

        st.subheader("📊 Technical Summary")
        summary = generate_technical_summary(df)
        st.code(summary)

        st.subheader("🤖 GPT Sentiment Analysis")
        gpt_response = ask_gpt(summary)
        st.success(gpt_response)
    else:
        st.error("No data found for that ticker/timeframe.")

