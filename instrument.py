from kiteconnect import KiteConnect
from dotenv import load_dotenv
# Assuming you already set API key + access token
import os 
import pandas as pd

load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
access_token = os.getenv("ACCESS_TOKEN")

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

print("Fetching instruments dump...")
instruments = kite.instruments()

# --- Convert to DataFrame ---
df = pd.DataFrame(instruments)

# --- Filter only NSE equity (EQ) ---
nse_eq = df[(df["exchange"] == "NSE") & (df["instrument_type"] == "EQ")]

# --- Save to CSV ---
nse_eq.to_csv("instruments.csv", index=False)

print("Saved NSE equity instruments:", len(nse_eq))
print("Sample symbols:", nse_eq["tradingsymbol"].head(10).tolist())