def print_clickable_stock(symbol: str, token: int, exchange: str = "NSE"):
    """
    Prints only the symbol as a clickable Zerodha Kite link (no visible URL).
    Works in VS Code terminal.
    """
    url = f"https://kite.zerodha.com/markets/chart/web/tvc/{exchange}/{symbol}/{token}"
    clickable_symbol = f"\033]8;;{url}\033\\{symbol}\033]8;;\033\\"
    print(clickable_symbol)
    print(url)

# Example
print_clickable_stock("TCS", 2953217)
