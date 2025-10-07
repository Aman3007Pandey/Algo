from datetime import datetime, timedelta
import os

LOG_PREFIX = "momentum_signals.log"
DYNAMIC_LOG_PREFIX="dynamic_signals"

def log_momentum_signal(candle, vol_cutoff,fileSuffix,avg_volume_of_this_stock,turnover,dayHigh):
    """
    Logs a momentum signal to a readable text file.
    
    Parameters:
    - candle: dict with keys 'name', 'close', 'volume_1_min'
    - volume_condition: bool or string describing volume condition
    """
    CRITERIA_MAP = {
    1: "50%",
    2: "45%",
    3: "40%",
    4: "35%",
    5: "Dynamic"
    }

    potential_gain = ((candle["ucl"] - candle["close"]) / candle["close"]) * 100
    potential_gain=round(potential_gain,2)

    criteria = CRITERIA_MAP.get(fileSuffix, "Unknown")
    suffix = DYNAMIC_LOG_PREFIX if fileSuffix == 5 else LOG_PREFIX
    LOG_FILE = f"{datetime.now().strftime('%Y-%m-%d')}_{suffix}.log"
    now = datetime.now().replace(second=0, microsecond=0)
    final_time = now - timedelta(minutes=1)

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write(f"{'Time':<20} {'Symbol':<12} {'Volume':<10} {'VolCutoff':<10}" f"{'Criteria':<10} {'turnover':<10} {'Days High':<9} {'%UC':<5} \n")
    with open(LOG_FILE, "a") as f:
        f.write(
            f"{final_time.strftime('%Y-%m-%d %H:%M:%S'):<20} "
            f"{candle['name']:<12} "
            f"{candle['volume_1_min']:<10} "
            f"{vol_cutoff:<10}"
            f"{criteria:<10}"
            f"{turnover:<11}"
            f"{dayHigh:<9}"
            f"{potential_gain:<5}\n"
            # f"{'LOW VOLUME' if avg_volume_of_this_stock < 150_000 else ''}\n"
        )


# sample_candle = {
#     "name": "RELIANCE",
#     "close": 2524.5,
#     "volume_1_min": 18250
# }

# log_momentum_signal(sample_candle,20000,1)
# log_momentum_signal(sample_candle,20000,2)
# log_momentum_signal(sample_candle,20000,1)
# log_momentum_signal(sample_candle,20000,1)

