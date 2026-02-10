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
df = pd.read_csv("instruments_1HOUR_volume.csv")

filtered = df[df["total_volume"] > df["avg_volume"]]
df = df[75000 < df["avg_volume"]]

print(df)

df.to_csv("instruments_1HOUR_volume.csv", index=False)

