import os
import pandas as pd

data_dir = "data"
fixed_dir = "data/fixed"
os.makedirs(fixed_dir, exist_ok=True)

for file in os.listdir(data_dir):
    if file.endswith(".csv"):
        try:
            path = os.path.join(data_dir, file)
            df = pd.read_csv(path)

            # Drop rows where 'Close' is not a number
            df = df[pd.to_numeric(df['Close'], errors='coerce').notnull()]

            # Convert Date column to datetime and set index
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)

            # Save cleaned file
            fixed_path = os.path.join(fixed_dir, file)
            df.to_csv(fixed_path)
            print(f"✅ Cleaned and saved: {fixed_path}")
        except Exception as e:
            print(f"❌ Failed to clean {file}: {e}")

