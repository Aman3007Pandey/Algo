import pandas as pd

# --- Step 1: Load your existing instruments.csv ---
df = pd.read_csv("instruments.csv")
print("Original records:", len(df))

# --- Step 2: Keep only NSE equity stocks ---  segment
df = df[(df["exchange"] == "NSE") & (df["instrument_type"] == "EQ") & (df["segment"] == "NSE")]

# --- Step 3: Remove junk (bonds, SDLs, ETFs, REITs, etc.) ---
# Common junk have '-' in tradingsymbol (like SDL-SG, ETFs with -IV, bonds with -N1, etc.)
df = df[df["tradingsymbol"].str.contains("-", na=False)]

# --- Step 4: Drop rows with missing names (if any) ---
df = df[~df["tradingsymbol"].str.match(r"^\d")]

columns_to_keep = ["instrument_token", "exchange_token", "tradingsymbol", "name", "last_price"]
df_clean = df[columns_to_keep]

# --- Step 5: Save the cleaned version ---
df_clean.to_csv("instruments_hypen.csv", index=False)



print("Filtered NSE company stocks:", len(df_clean))
print("Sample symbols:", df_clean["tradingsymbol"].head(10).tolist())
