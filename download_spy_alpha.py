import requests
import pandas as pd
import time
import os

API_KEY = "RFUV14ZO5B037CVE"
SYMBOL = "SPY"
BASE_URL = "https://www.alphavantage.co/query"
SAVE_PATH = "data/fixed"

os.makedirs(SAVE_PATH, exist_ok=True)

TIMEFRAMES = {
    "1d": {
        "function": "TIME_SERIES_DAILY",
        "interval": None,
        "outputsize": "compact",
        "key": "Time Series (Daily)",
        "filename": f"{SYMBOL}_1d.csv",
    },
    "1h": {
        "function": "TIME_SERIES_INTRADAY",
        "interval": "60min",
        "outputsize": "full",
        "key": "Time Series (60min)",
        "filename": f"{SYMBOL}_1h.csv",
    },
    "15m": {
        "function": "TIME_SERIES_INTRADAY",
        "interval": "15min",
        "outputsize": "full",
        "key": "Time Series (15min)",
        "filename": f"{SYMBOL}_15m.csv",
    },
}


def fetch_and_save_data(timeframe, config):
    params = {
        "function": config["function"],
        "symbol": SYMBOL,
        "apikey": API_KEY,
        "datatype": "json",
    }

    if config["interval"]:
        params["interval"] = config["interval"]
    if config["outputsize"]:
        params["outputsize"] = config["outputsize"]

    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        print(f"❌ HTTP Error: {response.status_code}")
        return

    data = response.json()
    if config["key"] not in data:
        print(f"❌ Failed to fetch {config['filename']} — Response: {data}")
        return

    time_series = data[config["key"]]
    df = pd.DataFrame.from_dict(time_series, orient="index")
    df.index.name = "Datetime"
    df = df.reset_index()

    # Rename columns dynamically to match app expectations
    df = df.rename(columns={
        df.columns[1]: "Open",
        df.columns[2]: "High",
        df.columns[3]: "Low",
        df.columns[4]: "Close",
        df.columns[5]: "Volume"
    })

    # Convert datatypes
    df["Datetime"] = pd.to_datetime(df["Datetime"])
    numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

    # Sort ascending by time
    df = df.sort_values("Datetime", ascending=True)

    # Save
    output_path = os.path.join(SAVE_PATH, config["filename"])
    df.to_csv(output_path, index=False)
    print(f"✅ Saved {config['filename']} to {output_path}")


# Main loop
for tf, cfg in TIMEFRAMES.items():
    fetch_and_save_data(tf, cfg)
    time.sleep(15)  # Pause to avoid hitting API limits


