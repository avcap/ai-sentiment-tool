import pandas as pd
import os

folder = "/Users/acap/ai-sentiment-tool/data/fixed"
files = ["SPY_1d.csv", "SPY_1h.csv", "SPY_15m.csv"]

for file in files:
    path = os.path.join(folder, file)
    print(f"Fixing: {file}")
    
    # Read the file, skipping the first 2 rows
    df = pd.read_csv(path, skiprows=2)

    # Rename the first unnamed column to "Datetime"
    if "Unnamed: 0" in df.columns:
        df.rename(columns={"Unnamed: 0": "Datetime"}, inplace=True)
    elif df.columns[0] != "Datetime":
        df.rename(columns={df.columns[0]: "Datetime"}, inplace=True)

    # Convert and set index
    df["Datetime"] = pd.to_datetime(df["Datetime"], errors="coerce")
    df.set_index("Datetime", inplace=True)
    df = df.sort_index()

    # Save cleaned file
    df.to_csv(path)
    print(f"✔ Cleaned and saved: {file}")

