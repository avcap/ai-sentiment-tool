import yfinance as yf
import time
import os


tickers = ["SPY", "NVDA"]
intervals = ["1d", "1h", "15m", "5m"]  # adjust based on what you want
period = "2d"  # for intraday, or use start/end for '1d'

def download_with_retry(ticker, interval, retries=3, delay=10):
    for attempt in range(retries):
        try:
            print(f"Downloading {ticker} at {interval} (Attempt {attempt+1})...")
            df = yf.download(ticker, period=period, interval=interval, progress=False)
            if df.empty:
                raise ValueError("Empty DataFrame returned")
            df.to_csv(f"data/{ticker}_{interval}.csv")
            print(f"✅ Saved to data/{ticker}_{interval}.csv\n")
            return
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(delay)
    print(f"❗ Failed to download {ticker} after {retries} retries.\n")

# Loop through all symbols and intervals
for ticker in tickers:
    for interval in intervals:
        download_with_retry(ticker, interval)
        time.sleep(15)  # space out requests more to avoid IP ban

