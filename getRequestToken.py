from kiteconnect import KiteConnect
from dotenv import load_dotenv
import os 

load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
access_token = os.getenv("ACCESS_TOKEN")


kite = KiteConnect(api_key=api_key)

# This is the URL you must open in your browser
print(kite.login_url())