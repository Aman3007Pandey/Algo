from kiteconnect import KiteConnect
from dotenv import load_dotenv
import os

# Load keys from env/config

load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
login_token=os.getenv("LOGIN_TOKEN")

kite = KiteConnect(api_key=api_key)

# After login, you get request_token in the redirect URL
request_token = login_token
# Generate session (exchange request_token for access_token)
data = kite.generate_session(request_token, api_secret=api_secret)

# Save this for reuse (important!)
access_token = data["access_token"]
kite.set_access_token(access_token)

print("Access token:", access_token)

env_path = ".env"   # change this if needed

# Read existing lines
lines = []
with open(env_path, "r") as f:
    lines = f.readlines()

# Write back with ACCESS_TOKEN replaced/added
with open(env_path, "w") as f:
    updated = False
    for line in lines:
        if line.startswith("ACCESS_TOKEN="):
            f.write(f"ACCESS_TOKEN={access_token}\n")
            updated = True
        else:
            f.write(line)

    # If ACCESS_TOKEN was not in the file, add it
    if not updated:
        f.write(f"\nACCESS_TOKEN={access_token}\n")