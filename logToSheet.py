import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime


SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", SCOPE
)

client = gspread.authorize(creds)

SPREADSHEET_NAME = "Week 7 LOGS"
WORKSHEET_NAME = "Feb11 "  

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
    link
):
    sheet.append_row([
        finalTime,
        symbol,
        quantity,
        resistance,
        vol_cutoff,
        high_low,
        uc_percent,
        link
    ], value_input_option="USER_ENTERED")


log_signal(
     "19:17"  ,
    symbol="ROLEXRINGS",
    quantity="YES",
    resistance=75.0,
    vol_cutoff=29551,
    high_low="high",
    uc_percent=16.72,
    link="https://kite.zerodha.com/markets/ext/chart/web/tvc/NSE/ROLEXRINGS/1351425"
)
