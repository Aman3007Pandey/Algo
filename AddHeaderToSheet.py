import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound
from datetime import datetime

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", SCOPE
)

client = gspread.authorize(creds)

SPREADSHEET_NAME = "MARCH LOGS"


now = datetime.now()
WORKSHEET_NAME = now.strftime("%B ") + str(now.day)

HEADER = [
    "Time",
    "Symbol",
    "Quantity",
    "Resistance",
    "VolCutoff",
    "High/Low",
    "%UC",
    "LV",
    "Link"
]

def get_or_create_sheet():
    # Spreadsheet
    try:
        sh = client.open(SPREADSHEET_NAME)
    except SpreadsheetNotFound:
        sh = client.create(SPREADSHEET_NAME)

    # Worksheet
    try:
        ws = sh.worksheet(WORKSHEET_NAME)
    except WorksheetNotFound:
        ws = sh.add_worksheet(
            title=WORKSHEET_NAME,
            rows=1000,
            cols=len(HEADER)
        )

    # Header
    existing = ws.row_values(1)
    if existing != HEADER:
        ws.clear()
        ws.insert_row(HEADER, 1)

    return ws

def force_text_columns(ws):
    # Columns A to H → TEXT
    ws.format("A:H", {
        "numberFormat": {
            "type": "TEXT"
        }
    })

    # Column H (Link) → URL (still works even as text)
    ws.format("I:I", {
        "numberFormat": {
            "type": "TEXT"
        }
    })


force_text_columns(get_or_create_sheet())
