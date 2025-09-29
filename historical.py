import pandas as pd
from kiteconnect import KiteConnect
import time
from dotenv import load_dotenv
import os 

load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
access_token = os.getenv("ACCESS_TOKEN")

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

# --- Load cleaned instruments CSV ---
df = pd.read_csv("instruments_clean.csv")
print("Total instruments:", len(df))

# --- Prepare output list ---
output = []

# --- Loop through each instrument ---
for idx, row in df.iterrows():
    symbol = row["tradingsymbol"]
    instrument_token = row["instrument_token"]
    try:
        # Fetch last 60 days daily historical data
        data = kite.historical_data(instrument_token,
                                    from_date="2025-07-20",
                                    to_date="2025-09-18",
                                    interval="day")
        if len(data) == 0:
            avg_vol = 0
        else:
            df_hist = pd.DataFrame(data)
            avg_vol = df_hist["volume"].mean()

        output.append({"tradingsymbol": symbol, "avg_volume": int(avg_vol)})
        print(f"{symbol}: avg_volume = {avg_vol:.0f}")

    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        output.append({"tradingsymbol": symbol, "avg_volume": 0})

    # --- Sleep to respect rate limits ---
    time.sleep(1)  # 1 second per request (so < 3/sec)

# --- Save to CSV ---
df_out = pd.DataFrame(output)
df_out.to_csv("instruments_avg_volume.csv", index=False)

print("Saved average volume for all instruments.")
