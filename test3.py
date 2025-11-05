from kiteconnect import KiteConnect
from dotenv import load_dotenv
import os 
import pandas as pd
from itertools import islice
from collections import deque
import time
from datetime import datetime
from requests.exceptions import RequestException
import urllib3
from logToCSV import log_momentum_signal
import math

load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
access_token = os.getenv("ACCESS_TOKEN")

# --- Kite setup ---
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

# --- Load avg volume CSV ---
df_avg = pd.read_csv("instruments_avg_volume.csv")
df_avg["instrument_token"] = df_avg["instrument_token"].astype(str)
symbols = df_avg["instrument_token"].tolist()
avg_volume_dict = dict(zip(df_avg["instrument_token"], df_avg["avg_volume"]))
token_to_symbol = dict(zip(df_avg["instrument_token"], df_avg["tradingsymbol"]))
day_high_map = {}
volume_map = {symbol: 0 for symbol in symbols}

# --- Filter high-volume stocks (>20k avg) ---
symbols = [s for s in symbols if avg_volume_dict[s] >= 20000]

# --- Initialize rolling data storage ---
stock_data = {s: deque(maxlen=3) for s in symbols}
volume_data= {s: deque(maxlen=60) for s in symbols}

# --- Chunk function for 500 symbols ---
def chunk_symbols(symbols, size=500):
    for i in range(0, len(symbols), size):
        yield symbols[i:i+size]




def safe_quote(kite, batch, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return kite.quote(batch)
        except (RequestException, urllib3.exceptions.ProtocolError, Exception) as e:
            print(f"Error fetching quotes (attempt {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(delay * (2 ** attempt))  # exponential backoff
            else:
                raise


def volume_threshold_exponent(avg_vol, a=2.08e+01, b=0.65):
    threshold = a * (avg_vol ** b)
    return round(threshold,0)

def volume_threshold_logarthmic(avg_vol, a=234566.11, b=-2813082.21):
    threshold = a*math.log(avg_vol)+b
    return round(threshold,0)

def findIfDayHigh(high,close):
    relative_closeness = (c3["high"] -  c3["close"]) / c3["high"]   
    threshold = 0.01  
    dayHigh = "yes" if relative_closeness <= threshold else "no"
    return dayHigh

def zerodhaLink(symbol: str, token: int, exchange: str = "NSE"):
    """
    Prints only the symbol as a clickable Zerodha Kite link (no visible URL).
    Works in VS Code terminal.
    """
    url = f"https://kite.zerodha.com/markets/ext/chart/web/tvc/{exchange}/{symbol}/{token}"
    return url

# --- Infinite loop for 1-minute candles ---
count=1
unusualVolumeSymbols=set()

while True:
    all_quotes = {}
    now = datetime.now()
    seconds_to_next_minute = 60 - now.second - now.microsecond / 1_000_000
    time.sleep(seconds_to_next_minute)
    
    print(f"Minute Start {count} | Time: {datetime.now().strftime('%H:%M:%S')}")
    for batch in chunk_symbols(symbols, 500):
        quotes = safe_quote(kite,batch)
        all_quotes.update(quotes)
        time.sleep(1)  # respect 3 requests/sec limit
    
    for token, data in all_quotes.items():
      
        symbol = token_to_symbol[token]
        
        candle = {"open": data["ohlc"]["open"], "close": data["last_price"], "volume_1_min": data["volume"], "cummulative_volume": data["volume"],"name":symbol,"high":data["ohlc"]["high"],"ucl":data["upper_circuit_limit"]} 

        if len(stock_data[token]) > 0:
            last_candle = stock_data[token][-1]
            candle["open"] = last_candle["close"]
            candle["volume_1_min"]=candle["cummulative_volume"]-last_candle["cummulative_volume"]

        if len(stock_data[token])==0:
            volume_map[symbol]=0

        stock_data[token].append(candle)

        # Handling rolling volume
        previousVolume=volume_data[token][0] if len(volume_data[token])==60 else 0
        volume_data[token].append(candle["cummulative_volume"])

                    

        # --- Check momentum criteria ---
        if len(stock_data[token]) == 3:
            c1, c2, c3 = stock_data[token]

            avg_volume_of_this_stock=avg_volume_dict[token]
            symbol=token_to_symbol[token]
            current_time = datetime.now().strftime("%H:%M")

            if c3["cummulative_volume"]-previousVolume>avg_volume_of_this_stock and token not in unusualVolumeSymbols:
                turnover=round((c3["volume_1_min"]*c3["close"])/1000,0)
                dayHigh=findIfDayHigh(c3["high"],c3["close"])
                link=zerodhaLink(symbol,token)
                if turnover>1000 and dayHigh=="yes":
                    # log_momentum_signal(candle,avg_volume_of_this_stock,0,c3["cummulative_volume"],turnover,dayHigh,link)
                    unusualVolumeSymbols.add(token)
                                  
    # Wait until next minute             
    print(f"Minute End {count} | Time: {datetime.now().strftime('%H:%M:%S')}")
    count=count+1                  
    
