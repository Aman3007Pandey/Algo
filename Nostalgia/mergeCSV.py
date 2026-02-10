import pandas as pd

df_clean = pd.read_csv("instruments_clean.csv")
df_avg = pd.read_csv("instruments_avg_volume.csv")

df_merged = df_clean.merge(df_avg, on="tradingsymbol", how="inner")
df_final = df_merged[["instrument_token", "tradingsymbol", "avg_volume"]]
print(df_final.head())

df_final.to_csv("instruments_avg_volume.csv", index=False)

print(f"Final file saved with {len(df_final)} rows.")
