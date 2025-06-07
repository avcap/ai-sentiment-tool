

# app.py
import streamlit as st
from data_utils import get_price_data, generate_technical_summary, generate_gpt_sentiment

st.set_page_config(page_title="AI Chart Sentiment Tool", layout="wide")

st.title("📈 AI Chart Sentiment Tool")
st.markdown("Select a ticker, interval, and available date range to analyze.")

# File config
data_dir = "data/fixed"

ticker = st.selectbox("Select Ticker", ["SPY"])
interval = st.selectbox("Select Interval", ["1d", "1h", "15m"])

# Load data
with st.spinner("Loading data..."):
    df = get_price_data(ticker, interval, data_dir=data_dir)

if df.empty:
    st.error("No data found. Please check your CSV or interval.")
    st.stop()

# Show date range available
date_options = df.index.strftime("%Y-%m-%d").unique().tolist()
start_date = st.selectbox("Start Date", date_options, index=0)
end_date = st.selectbox("End Date", date_options, index=len(date_options)-1)

# Filter dataframe to date range
filtered_df = df.loc[start_date:end_date]

st.subheader("📊 Chart Preview")
st.dataframe(filtered_df.tail(10))

# Show technical summary
summary = generate_technical_summary(filtered_df)
st.markdown("### 🧠 Technical Summary")
st.code(summary)

# Show GPT Sentiment
st.markdown("### 🤖 GPT Sentiment")
try:
    sentiment = generate_gpt_sentiment(summary)
    st.success(sentiment)
except Exception as e:
    st.error(f"Error getting GPT response:\n{str(e)}")


