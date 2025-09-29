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

# --- Filter high-volume stocks (>20k avg) ---
symbols = [s for s in symbols if avg_volume_dict[s] >= 20000]

# --- Initialize rolling data storage ---
stock_data = {s: deque(maxlen=3) for s in symbols}

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


def volume_threshold(avg_vol, a=2.08e+01, b=0.65):
    threshold = a * (avg_vol ** b)
    return threshold

# --- Infinite loop for 1-minute candles ---
count=1
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
        # last_price = data['last_price']
        # volume = data['volume']
        symbol = token_to_symbol[token]
        # print(symbol,last_price,volume)
        candle = {"open": data["ohlc"]["open"], "close": data["last_price"], "volume_1_min": data["volume"], "cummulative_volume": data["volume"],"name":symbol}        
        if len(stock_data[token]) > 0:
            last_candle = stock_data[token][-1]
            candle["open"] = last_candle["close"]
            candle["volume_1_min"]=candle["cummulative_volume"]-last_candle["cummulative_volume"]

        stock_data[token].append(candle)    

        # --- Check momentum criteria ---
        if len(stock_data[token]) == 3:
            c1, c2, c3 = stock_data[token]
            
            # 3 green candles
            if c1["close"] > c1["open"] and c2["close"] > c2["open"] and c3["close"] > c3["open"]:
                # volume checks

                avg_volume_of_this_stock=avg_volume_dict[token]
                avg_volume_curr_check_1=0.5*avg_volume_of_this_stock
                avg_volume_curr_check_2=0.45*avg_volume_of_this_stock
                avg_volume_curr_check_3=0.40*avg_volume_of_this_stock
                avg_volume_curr_check_4=0.35*avg_volume_of_this_stock

                if c3["volume_1_min"] > max(c1["volume_1_min"], c2["volume_1_min"]) and c3["volume_1_min"] >=avg_volume_curr_check_1:
                    print(f"Momentum signal: {c3['name']} Volume : {c3['volume_1_min']} VolumeCondition : {avg_volume_curr_check_1}")
                    # print(f"Momentum signal: {c3['name']} Volume : {c2['volume_1_min']} Volume : {c1['volume_1_min']}")
                    log_momentum_signal(candle,avg_volume_curr_check_1,1,avg_volume_of_this_stock)
                elif c3["volume_1_min"] > max(c1["volume_1_min"], c2["volume_1_min"]) and c3["volume_1_min"] >=avg_volume_curr_check_2:
                    log_momentum_signal(candle,avg_volume_curr_check_2,2,avg_volume_of_this_stock)
                elif c3["volume_1_min"] > max(c1["volume_1_min"], c2["volume_1_min"]) and c3["volume_1_min"] >=avg_volume_curr_check_3:
                    log_momentum_signal(candle,avg_volume_curr_check_3,3,avg_volume_of_this_stock)
                elif c3["volume_1_min"] > max(c1["volume_1_min"], c2["volume_1_min"]) and c3["volume_1_min"] >=avg_volume_curr_check_4:
                    log_momentum_signal(candle,avg_volume_curr_check_4,4,avg_volume_of_this_stock)
                    print(f"Momentum signal: {c3['name']} Volume : {c3['volume_1_min']} VolumeCondition : {avg_volume_curr_check_4}")              

                avg_volume_curr_check_5=volume_threshold(avg_volume_of_this_stock)
                if c3["volume_1_min"] > max(c1["volume_1_min"], c2["volume_1_min"]) and c3["volume_1_min"] >=avg_volume_curr_check_5:
                    log_momentum_signal(candle,avg_volume_curr_check_5,5,avg_volume_of_this_stock)
    # Wait until next minute             
    print(f"Minute End {count} | Time: {datetime.now().strftime('%H:%M:%S')}")
    count=count+1                  
    
