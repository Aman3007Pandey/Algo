import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound


SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", SCOPE
)

client = gspread.authorize(creds)

SPREADSHEET_NAME = "Week 7 LOGS"
WORKSHEET_NAME = "Feb11"  

HEADER = [
    "Time",
    "Symbol",
    "Quantity",
    "Resistance",
    "VolCutoff",
    "High/Low",
    "%UC",
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
    # Columns A to G → TEXT
    ws.format("A:G", {
        "numberFormat": {
            "type": "TEXT"
        }
    })

    # Column H (Link) → URL (still works even as text)
    ws.format("H:H", {
        "numberFormat": {
            "type": "TEXT"
        }
    })


force_text_columns(get_or_create_sheet())
