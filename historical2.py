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
df = pd.read_csv("instruments_avg_volume.csv")
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
                                    from_date="2025-10-20 09:15:00",
                                    to_date="2025-10-20 10:15:00",
                                    interval="60minute")
        if len(data) == 0:
            total_vol = 0
        else:
            df_hist = pd.DataFrame(data)
            total_vol = df_hist["volume"].iloc[0]

        if total_vol>=row["avg_volume"] and total_vol>=75000:    
            output.append({"tradingsymbol": symbol, "total_volume": int(total_vol) , "avg_volume":int(row["avg_volume"])})
            print(symbol)
        # print(f"{symbol}: total_volume = {total_vol}"
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")

    # --- Sleep to respect rate limits ---
    time.sleep(0.4)  # 1 second per request (so < 3/sec)

# --- Save to CSV ---
df_out = pd.DataFrame(output)
df_out.to_csv("instruments_1HOUR_volume.csv", index=False)

print("Saved average volume for all instruments.")
