def print_clickable_stock(symbol: str, token: int, exchange: str = "NSE"):
    """
    Prints only the symbol as a clickable Zerodha Kite link (no visible URL).
    Works in VS Code terminal.
    """
    url = f"https://kite.zerodha.com/markets/ext/chart/web/tvc/{exchange}/{symbol}/{token}"
    
    print(url)

# Example
print_clickable_stock("TCS", 2953217)
print_clickable_stock("APOLLOTYRE", 41729)
