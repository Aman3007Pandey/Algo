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
from logToCSV import log_momentum_signal,log_test_momentum_signal
import math
import pytz

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

# --- Infinite loop for 1-minute candles ---
count=1
unusualVolumeSymbols=set()
india = pytz.timezone("Asia/Kolkata")

while True:
    all_quotes = {}
    # now = datetime.now()
    now = datetime.now(india)
    seconds_to_next_minute = 60 - now.second - now.microsecond / 1_000_000
    time.sleep(seconds_to_next_minute)
    
    print(f"Minute Start {count} | Time: {datetime.now(india).strftime('%H:%M:%S')}")
    for batch in chunk_symbols(symbols, 500):
        quotes = safe_quote(kite,batch)
        all_quotes.update(quotes)
        time.sleep(1)  # respect 3 requests/sec limit
    
    for token, data in all_quotes.items():
        # last_price = data['last_price']
        # volume = data['volume']
        symbol = token_to_symbol[token]
        # print(symbol,last_price,volume)
        candle = {"open": data["ohlc"]["open"], "close": data["last_price"], "volume_1_min": data["volume"], "cummulative_volume": data["volume"],"name":symbol,"high":data["ohlc"]["high"],"ucl":data["upper_circuit_limit"]}        
        if len(stock_data[token]) > 0:
            last_candle = stock_data[token][-1]
            candle["open"] = last_candle["close"]
            candle["volume_1_min"]=candle["cummulative_volume"]-last_candle["cummulative_volume"]


        stock_data[token].append(candle)    

        # --- Check momentum criteria ---
        if len(stock_data[token]) == 3:
            c1, c2, c3 = stock_data[token]

            # log_test_momentum_signal()
            avg_volume_of_this_stock=avg_volume_dict[token]
            current_time = datetime.now(india).time()
            cutoff_time1 = datetime.strptime("10:00", "%H:%M").time()
            cutoff_time2 = datetime.strptime("11:00", "%H:%M").time()
            cutoff_time3 = datetime.strptime("12:00", "%H:%M").time()
            cutoff_time4 = datetime.strptime("13:00", "%H:%M").time()
            if current_time<cutoff_time1 and c3["cummulative_volume"]>avg_volume_of_this_stock and token not in unusualVolumeSymbols:
                turnover=round((c3["volume_1_min"]*c3["close"])/1000,0)
                dayHigh=findIfDayHigh(c3["high"],c3["close"])
                if turnover>1000 and dayHigh=="yes":
                    log_momentum_signal(candle,avg_volume_of_this_stock,0,c3["cummulative_volume"],turnover,dayHigh)
                    unusualVolumeSymbols.add(token)
            elif current_time<cutoff_time2 and c3["cummulative_volume"]>2*avg_volume_of_this_stock and token not in unusualVolumeSymbols:
                turnover=round((c3["volume_1_min"]*c3["close"])/1000,0)
                dayHigh=findIfDayHigh(c3["high"],c3["close"])
                if turnover>1000 and dayHigh=="yes":
                    log_momentum_signal(candle,avg_volume_of_this_stock,0,c3["cummulative_volume"],turnover,dayHigh)
                    unusualVolumeSymbols.add(token)
            elif current_time<cutoff_time3 and c3["cummulative_volume"]>3*avg_volume_of_this_stock and token not in unusualVolumeSymbols:
                turnover=round((c3["volume_1_min"]*c3["close"])/1000,0)
                dayHigh=findIfDayHigh(c3["high"],c3["close"])
                if turnover>1000 and dayHigh=="yes":
                    log_momentum_signal(candle,avg_volume_of_this_stock,0,c3["cummulative_volume"],turnover,dayHigh)
                    unusualVolumeSymbols.add(token)
            elif current_time<cutoff_time4 and c3["cummulative_volume"]>4*avg_volume_of_this_stock and token not in unusualVolumeSymbols:
                turnover=round((c3["volume_1_min"]*c3["close"])/1000,0)
                dayHigh=findIfDayHigh(c3["high"],c3["close"])
                if turnover>1000 and dayHigh=="yes":
                    log_momentum_signal(candle,avg_volume_of_this_stock,0,c3["cummulative_volume"],turnover,dayHigh)
                    unusualVolumeSymbols.add(token)                         


            
            # 3 green candles
            if c1["close"] > c1["open"] and c2["close"] > c2["open"] and c3["close"] > c3["open"]:
                # volume checks

                
                avg_volume_curr_check_1=round(0.5*avg_volume_of_this_stock,0)
                avg_volume_curr_check_2=round(0.45*avg_volume_of_this_stock,0)
                avg_volume_curr_check_3=round(0.40*avg_volume_of_this_stock,0)
                avg_volume_curr_check_4=round(0.35*avg_volume_of_this_stock,0)
                turnover=round((c3["volume_1_min"]*c3["close"])/1000,0)

                dayHigh=findIfDayHigh(c3["high"],c3["close"])

                if min(c1["volume_1_min"] , c2["volume_1_min"]) < 1200:
                    continue

                if c3["volume_1_min"] > max(c1["volume_1_min"], c2["volume_1_min"]) and c3["volume_1_min"] >=avg_volume_curr_check_1:
                    print(f"Momentum signal: {c3['name']} Volume : {c3['volume_1_min']} VolumeCondition : {avg_volume_curr_check_1}")
                    # print(f"Momentum signal: {c3['name']} Volume : {c2['volume_1_min']} Volume : {c1['volume_1_min']}")
                    log_momentum_signal(candle,avg_volume_curr_check_1,1,candle["volume_1_min"],turnover,dayHigh)
                elif c3["volume_1_min"] > max(c1["volume_1_min"], c2["volume_1_min"]) and c3["volume_1_min"] >=avg_volume_curr_check_2:
                    log_momentum_signal(candle,avg_volume_curr_check_2,2,candle["volume_1_min"],turnover,dayHigh)
                elif c3["volume_1_min"] > max(c1["volume_1_min"], c2["volume_1_min"]) and c3["volume_1_min"] >=avg_volume_curr_check_3:
                    log_momentum_signal(candle,avg_volume_curr_check_3,3,candle["volume_1_min"],turnover,dayHigh)
                elif c3["volume_1_min"] > max(c1["volume_1_min"], c2["volume_1_min"]) and c3["volume_1_min"] >=avg_volume_curr_check_4:
                    log_momentum_signal(candle,avg_volume_curr_check_4,4,candle["volume_1_min"],turnover,dayHigh)
        
                avg_volume_curr_check_5=volume_threshold_logarthmic(avg_volume_of_this_stock)
                if c3["volume_1_min"] > max(c1["volume_1_min"], c2["volume_1_min"]) and c3["volume_1_min"] >=avg_volume_curr_check_5:   
                        log_momentum_signal(candle,avg_volume_curr_check_5,6,candle["volume_1_min"],turnover,dayHigh)
    # Wait until next minute             
    print(f"Minute End {count} | Time: {datetime.now(india).strftime('%H:%M:%S')}")
    count=count+1                  
    
