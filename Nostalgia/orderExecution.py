from kiteconnect import KiteConnect
import math
from dotenv import load_dotenv
import os


load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
access_token = os.getenv("ACCESS_TOKEN")

# --- Kite setup ---
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

CASH_CAPITAL = 2000        # Rupees in your account you want to risk for this setup
INTRADAY_LEVERAGE = 5      # 5x MIS
STOPLOSS_PCT = 1.5         # 1.5%

TICK_SIZE = 0.05           # most NSE equities; adjust if needed


def round_to_tick(price, tick=TICK_SIZE):
    return round(round(price / tick) * tick, 2)


def place_intraday_buy_with_sl(
    tradingsymbol: str,
    exchange: str,
    entry_price: float,
    cash_capital: float = CASH_CAPITAL,
    leverage: float = INTRADAY_LEVERAGE,
    sl_pct: float = STOPLOSS_PCT,
):
    # 1) Calculate quantity using cash * leverage
    exposure = cash_capital * leverage
    qty = int(exposure // entry_price)
    if qty <= 0:
        raise ValueError("Quantity calculated as 0. Increase cash or reduce price.")

    # 2) Calculate SL price = 1.5% below entry
    raw_sl = entry_price * (1 - sl_pct / 100.0)
    sl_price = round_to_tick(raw_sl)

    # For SL LIMIT order Zerodha requires: price >= trigger_price
    trigger_price = sl_price

    # 3) Place MIS LIMIT BUY
    buy_order_id = kite.place_order(
        variety=kite.VARIETY_REGULAR,
        exchange=exchange,
        tradingsymbol=tradingsymbol,
        transaction_type=kite.TRANSACTION_TYPE_BUY,
        quantity=qty,
        product=kite.PRODUCT_MIS,
        order_type=kite.ORDER_TYPE_LIMIT,
        price=entry_price,
    )

    # 4) Place MIS SELL SL order for stop-loss
    sl_order_id = kite.place_order(
        variety=kite.VARIETY_REGULAR,
        exchange=exchange,
        tradingsymbol=tradingsymbol,
        transaction_type=kite.TRANSACTION_TYPE_SELL,
        quantity=qty,
        product=kite.PRODUCT_MIS,
        order_type=kite.ORDER_TYPE_SL,   # stop-loss LIMIT
        price=sl_price,                  # limit price
        trigger_price=trigger_price,     # trigger price
    )

    return buy_order_id, sl_order_id

def one_click_cli():
    symbol = ""
    exchange = "NSE"  # or detect based on symbol
    entry_price = 0.00

    buy_id, sl_id = place_intraday_buy_with_sl(symbol, exchange, entry_price)
    print(f"Done ✅ BUY: {buy_id}, SL: {sl_id}")


if __name__ == "__main__":
    one_click_cli()
