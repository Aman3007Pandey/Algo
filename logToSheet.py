import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import requests
import time


SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", SCOPE
)

client = gspread.authorize(creds)

SPREADSHEET_NAME = "APRIL LOGS"
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
