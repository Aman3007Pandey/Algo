from datetime import datetime, timedelta
import os
import pytz
from historicalPrice import fetch_last_10_days_ohlc
from logToSheet import log_signal

def log_momentum_signal(candle, vol_cutoff,fileSuffix,longorShort,link,token):
    """
    Logs a momentum signal to a readable text file.
    
    Parameters:
    - candle: dict with keys 'name', 'close', 'volume_1_min'
    - volume_condition: bool or string describing volume condition
    """

    india = pytz.timezone("Asia/Kolkata")
    

    potential_gain = ((candle["ucl"] - candle["close"]) / candle["close"]) * 100
    potential_gain=round(potential_gain,2)

    now = datetime.now(india).replace(second=0, microsecond=0)
    final_time = now - timedelta(minutes=1)
    new_price = (candle["close"] * 101) // 100   # price + 1% buffer
    money = 10000

    if(new_price<=0):
        new_price=1
        
    qty = money // new_price    # floor quantity

    SetupType='A+'
    (hisLow,hisHigh)=fetch_last_10_days_ohlc(token)

    if hisLow==None:
        SetupType='Historical Failed'
    elif longorShort =='high' and  ( hisHigh>(candle["close"] * 104) // 100 ):
        SetupType='PNQ'
    elif longorShort =='low' and (hisLow<(candle["close"] * 96) // 100):
        SetupType='PNQ'
    elif longorShort =='high' and (hisHigh>(candle["close"] * 102) // 100):
        SetupType='SRT'
    elif longorShort =='low' and (hisLow<(candle["close"] * 98) // 100):
        SetupType='SRT'                 

    logTime=str(final_time.strftime("%H:%M"))
    log_signal(logTime,candle['name'],qty,SetupType,vol_cutoff,longorShort,potential_gain,link)
    

# def log_test_momentum_signal():
#     candle1={
#         "ucl":245,
#         "close":270,
#         "name":"NYKAA"
#     }
#     candle2={
#         "ucl":245,
#         "close":66.03,
#         "name":"WEBELSOLAR"
#     }
#     candle3={
#         "ucl":245,
#         "close":878.45,
#         "name":"LICI"
#     }
#     candle4={
#         "ucl":245,
#         "close":981,
#         "name":"DREDGECORP"
#     }
#     candle5={
#         "ucl":245,
#         "close":589,
#         "name":"HINDCOPPER"
#     }
#     log_momentum_signal(candle1,4144141,0,"high","zerodha/link/"+candle1["name"],1675521)
#     log_momentum_signal(candle2,4144141,0,"low","zerodha/link/"+candle2["name"],3738113)
#     log_momentum_signal(candle3,4144141,0,"high","zerodha/link/"+candle3["name"],2426881)
#     log_momentum_signal(candle4,4144141,0,"high","zerodha/link/"+candle4["name"],2885377)
#     log_momentum_signal(candle5,4144141,0,"high","zerodha/link/"+candle5["name"],4592385)

# log_test_momentum_signal()