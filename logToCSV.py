from datetime import datetime, timedelta
import os
import pytz

FOLDER_PATH="today_logs"
LOG_PREFIX = "momentum_signals"
DYNAMIC_LOG_PREFIX="dynamic_signals"
VOLUME_LOG_PREFIX="volume_signals"

def log_momentum_signal(candle, vol_cutoff,fileSuffix,current_volume,turnover,dayHigh,link):
    """
    Logs a momentum signal to a readable text file.
    
    Parameters:
    - candle: dict with keys 'name', 'close', 'volume_1_min'
    - volume_condition: bool or string describing volume condition
    """
    CRITERIA_MAP = {
    0: "UV",    
    1: "50%",
    2: "45%",
    3: "40%",
    4: "35%",
    5: "UHV",
    6: "Dynamic"
    }

    india = pytz.timezone("Asia/Kolkata")
    

    potential_gain = ((candle["ucl"] - candle["close"]) / candle["close"]) * 100
    potential_gain=round(potential_gain,2)

    criteria = CRITERIA_MAP.get(fileSuffix, "Unknown")
    suffix = DYNAMIC_LOG_PREFIX if fileSuffix == 6 else VOLUME_LOG_PREFIX if fileSuffix == 0 else LOG_PREFIX
    LOG_FILE = f"{FOLDER_PATH}/{datetime.now(india).strftime('%Y-%m-%d')}_{suffix}.log"
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    now = datetime.now(india).replace(second=0, microsecond=0)
    final_time = now - timedelta(minutes=1)
    new_price = (candle["close"] * 101) // 100   # price + 1% buffer
    money = 10000
    qty = money // new_price    # floor quantity


    # if not os.path.exists(LOG_FILE):
    #     with open(LOG_FILE, "w") as f:
    #         f.write(f"{'Time':<20} {'Symbol':<12} {'Volume':<10} {'VolCutoff':<10}" f"{'Criteria':<10} {'turnover':<10} {'Days High':<9} {'%UC':<5} \n")
    # with open(LOG_FILE, "a") as f:
    #     f.write(
    #         f"{final_time.strftime('%Y-%m-%d %H:%M:%S'):<20} "
    #         f"{candle['name']:<12} "
    #         f"{current_volume:<10} "
    #         f"{vol_cutoff:<10}"
    #         f"{criteria:<10}"
    #         f"{turnover:<11}"
    #         f"{dayHigh if dayHigh is not None else 'NA':<9}"
    #         f"{potential_gain:<5}\n"
    #         # f"{'LOW VOLUME' if avg_volume_of_this_stock < 150_000 else ''}\n"
    #     )


    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write(f"{'Time':<10} {'Symbol':<12} {'Quantity':<10} {'VolCutoff':<10} {'Turnover':<12} {'%UC':<32} {'Link':<5}\n")

    with open(LOG_FILE, "a") as f:
        f.write(
            f"{final_time.strftime('%H:%M'):<10} "           # only hour and minute
            f"{candle['name']:<12} "
            f"{qty:<10} "
            f"{vol_cutoff:<10} "
            f"{turnover:<10} "
            f"{potential_gain:<5} "
            f"{link:<50}\n"
    )

def log_test_momentum_signal():
    candle={
        "ucl":245,
        "close":435,
        "name":"AMAN"
    }
    # log_momentum_signal(candle,4144141,0,43243,655676,"yes")

def zerodhaLink(symbol: str, token: int, exchange: str = "NSE"):
    """
    Prints only the symbol as a clickable Zerodha Kite link (no visible URL).
    Works in VS Code terminal.
    """
    url = f"https://kite.zerodha.com/markets/ext/chart/web/tvc/{exchange}/{symbol}/{token}"
    return url

# log_test_momentum_signal()