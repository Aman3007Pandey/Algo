from kiteconnect import KiteConnect
from dotenv import load_dotenv
# Assuming you already set API key + access token
import os 

load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
access_token = os.getenv("ACCESS_TOKEN")

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

# Get market quotes
# You can pass either "exchange:tradingsymbol" or numeric instrument_token
# Example: NSE:INFY or instrument_token 408065
symbols = ["NSE:INFY", "NSE:TCS", "NSE:RELIANCE"]

quotes = kite.quote(symbols)

for s, q in quotes.items():
    print(f"{s}: LTP = {q['last_price']}, Volume = {q['volume']}")