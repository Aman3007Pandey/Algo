from kiteconnect import KiteConnect
from dotenv import load_dotenv
import os

# Load keys from env/config

load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")


kite = KiteConnect(api_key=api_key)

# After login, you get request_token in the redirect URL
request_token = "PehymzddD7Uvcaf495NUt2vpNQxllvZ8"
# Generate session (exchange request_token for access_token)
data = kite.generate_session(request_token, api_secret=api_secret)

# Save this for reuse (important!)
access_token = data["access_token"]
kite.set_access_token(access_token)

print("Access token:", access_token)