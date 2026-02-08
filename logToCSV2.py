from datetime import datetime, timedelta
import os
import pytz
from historicalPrice import fetch_last_10_days_ohlc

FOLDER_PATH="today_logs"
LOG_PREFIX = "momentum_signals"
DYNAMIC_LOG_PREFIX="dynamic_signals"
VOLUME_LOG_PREFIX="volume_signals"

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

    suffix = DYNAMIC_LOG_PREFIX if fileSuffix == 6 else VOLUME_LOG_PREFIX if fileSuffix == 0 else LOG_PREFIX
    LOG_FILE = f"{FOLDER_PATH}/{datetime.now(india).strftime('%Y-%m-%d')}_{suffix}.log"
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    now = datetime.now(india).replace(second=0, microsecond=0)
    final_time = now - timedelta(minutes=1)
    new_price = (candle["close"] * 101) // 100   # price + 1% buffer
    money = 10000
    qty = money // new_price    # floor quantity

    isResistanceThere='NO'
    (hisLow,hisHigh)=fetch_last_10_days_ohlc(token)

    if longorShort =='high' and  ( hisHigh>(candle["close"] * 104) // 100 ):
        isResistanceThere='YES'
    elif longorShort =='low' and (hisLow<(candle["close"] * 96) // 100):
        isResistanceThere='YES'     


    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write(f"{'Time':<10} {'Resistance':<10} {'Quantity':<10} {'VolCutoff':<10} {'High/Low':<12} {'%UC':<32} {'Link':<5}\n")

    with open(LOG_FILE, "a") as f:
        f.write(
            f"{final_time.strftime('%H:%M'):<10} "           # only hour and minute
            f"{isResistanceThere:<10} "
            f"{qty:<10} "
            f"{vol_cutoff:<10} "
            f"{longorShort:<10} "
            f"{potential_gain:<5} "
            f"{link:<50}\n"
    )

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




def zerodhaLink(symbol: str, token: int, exchange: str = "NSE"):
    """
    Prints only the symbol as a clickable Zerodha Kite link (no visible URL).
    Works in VS Code terminal.
    """
    url = f"https://kite.zerodha.com/markets/ext/chart/web/tvc/{exchange}/{symbol}/{token}"
    return url

# log_test_momentum_signal()