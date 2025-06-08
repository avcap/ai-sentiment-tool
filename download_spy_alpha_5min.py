import requests
import pandas as pd
import time
import os

API_KEY = "RFUV14ZO5B037CVE"
SYMBOL = "SPY"
INTERVAL = "5min"
OUTPUT_SIZE = "compact"  # "compact" returns last ~2 days; "full" returns more but is rate-limited

url = "https://www.alphavantage.co/query"

params = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": SYMBOL,
    "interval": INTERVAL,
    "apikey": API_KEY,
    "outputsize": OUTPUT_SIZE,
    "datatype": "json"
}

print(f"📡 Requesting {SYMBOL} {INTERVAL} data from Alpha Vantage...")
response = requests.get(url, params=params)
data = response.json()

if f"Time Series ({INTERVAL})" not in data:
    print(f"❌ Failed to fetch data — Response: {data}")
else:
    time_series = data[f"Time Series ({INTERVAL})"]
    df = pd.DataFrame.from_dict(time_series, orient="index")
    df.index = pd.to_datetime(df.index)
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    df = df.sort_index()  # Ascending order (oldest first)
    df.index.name = "Datetime"

    output_path = "data/fixed/SPY_5m.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path)
    print(f"✅ Saved to {output_path}")

