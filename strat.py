import pandas as pd

# --- Load cleaned instruments CSV ---
df = pd.read_csv("instruments_avg_volume.csv")
print("Total instruments:", len(df))


count=0
# --- Loop through each instrument ---
for idx, row in df.iterrows():
    symbol = row["tradingsymbol"]
    avg_volume=row["avg_volume"]
    if avg_volume>25000:
        count=count+1

print("Instruments after Avg Volume Filter",count)

