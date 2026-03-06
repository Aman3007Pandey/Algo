from kiteconnect import KiteConnect
from dotenv import load_dotenv
import os 
import pandas as pd
from requests.exceptions import RequestException
from logToCSV import log_momentum_signal
import pytz
from datetime import datetime, timedelta
import time

load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
access_token = os.getenv("ACCESS_TOKEN")

# --- Kite setup ---
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)


def fetch_last_10_days_ohlc(token:int):
    """
    Fetch last 10 days of daily OHLC data for an NSE stock.
    
    Args:
        stock_symbol (str): Trading symbol (e.g. 'RELIANCE', 'TCS')
        
    Returns:
        pd.DataFrame
    """

    try:    
        india = pytz.timezone("Asia/Kolkata")

        # 2️⃣ Date range
        to_date = datetime.now(india).date()
        from_date = to_date - timedelta(days=10)
        to_date=to_date-timedelta(days=1)

        # 3️⃣ Fetch historical data
        data = kite.historical_data(
            instrument_token=token,
            from_date=from_date,
            to_date=to_date,
            interval="day"
        )

        # 4️⃣ Convert to DataFrame
        df = pd.DataFrame(data)

        ten_day_low = df["low"].min()
        ten_day_high = df["high"].max()

        # print(ten_day_low,ten_day_high)
        time.sleep(1)
        return (ten_day_low,ten_day_high)

    except Exception as e:
        print(f"[WARN] Historical data fetch failed for {token}: {e}")
        return None, None


# fetch_last_10_days_ohlc(2885377)