import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import requests
import time

LOG_FOLDER = "today_logs"

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", SCOPE
)

client = gspread.authorize(creds)

SPREADSHEET_NAME = "MAY LOGS"
now = datetime.now()
WORKSHEET_NAME = now.strftime("%B ") + str(now.day)

sh = client.open(SPREADSHEET_NAME)
sheet = sh.worksheet(WORKSHEET_NAME)


def log_signal(
    finalTime,
    symbol,
    quantity,
    resistance,
    vol_cutoff,
    high_low,
    uc_percent,
    lv,
    link
):
    max_retries = 3
    base_delay = 1  # seconds

    row = [
        finalTime,
        symbol,
        quantity,
        resistance,
        vol_cutoff,
        high_low,
        uc_percent,
        lv,
        link
    ]

    for attempt in range(max_retries):
        try:
            sheet.append_row(
                row,
                value_input_option="USER_ENTERED"
            )
            return  # ✅ success → exit function

        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:

            delay = base_delay * (2 ** attempt)
            print(
                f"[WARN] Google Sheet write failed "
                f"(attempt {attempt + 1}/{max_retries}). "
                f"Retrying in {delay}s"
            )
            time.sleep(delay)

        except Exception as e:
            print(f"[ERROR] Sheet logging failed: {e}")
            print (row)
            return  #  unknown error → skip & continue algo

    # After retries exhausted
    print("[ERROR] Sheet unreachable. Skipping log and continuing algo.")


# log_signal(
#      "19:17"  ,
#     symbol="ROLEXRINGS",
#     quantity="YES",
#     resistance=75.0,
#     vol_cutoff=29551,
#     high_low="high",
#     uc_percent=16.72,
#     lv="YES"
#     link="https://kite.zerodha.com/markets/ext/chart/web/tvc/NSE/ROLEXRINGS/1351425"
# )


def log_signal2(
    finalTime,
    symbol,
    quantity,
    resistance,
    vol_cutoff,
    high_low,
    uc_percent,
    lv,
    link
):
    os.makedirs(LOG_FOLDER, exist_ok=True)
    log_file = os.path.join(LOG_FOLDER, f"{datetime.now().strftime('%Y-%m-%d')}_MAY_LOGS.log")

    time_value = (
        finalTime.strftime('%H:%M')
        if isinstance(finalTime, datetime)
        else str(finalTime)
    )

    if not os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(
                f"{'Time':<10} {'Symbol':<12} {'Quantity':<10} {'Resistance':<12} "
                f"{'VolCutoff':<10} {'High/Low':<12} {'%UC':<8} {'LV':<8} {'Link'}\n"
            )

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(
            f"{time_value:<10} "
            f"{symbol:<12} "
            f"{quantity:<10} "
            f"{resistance:<12} "
            f"{vol_cutoff:<10} "
            f"{high_low:<12} "
            f"{uc_percent:<8} "
            f"{lv:<8} "
            f"{link}\n"
        )

   