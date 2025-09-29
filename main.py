import os
from kiteconnect import KiteConnect
from dotenv import load_dotenv

def main():
    load_dotenv()
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")

    if not (api_key and api_secret and access_token):
        print("Please set API_KEY, API_SECRET, ACCESS_TOKEN in .env")
        return

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)

    # Example: fetch full quote of one instrument
    resp_quote = kite.quote("NSE:INFY")
    # 'resp_quote' is something like { 'NSE:INFY': { ... lots of fields ... } }
    print("Full quote for INFY:", resp_quote["NSE:INFY"])

    # Example: fetch LTP for many instruments
    symbols = ["NSE:INFY", "NSE:TCS", "NSE:RELIANCE"]
    resp_ltp = kite.ltp(*symbols)
    # kite.ltp returns: { 'NSE:INFY': {'last_price': ...}, 'NSE:TCS': ... }
    print("LTPs:", resp_ltp)

    # Example: fetch OHLC (open, high, low, close etc.)
    resp_ohlc = kite.ohlc(*symbols)
    print("OHLCs:", resp_ohlc)  # each symbol has ohlc inside

if __name__ == "__main__":
    main()
