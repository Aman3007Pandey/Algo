import pandas as pd

# === Input Files ===
LOG_FILE = "2025-10-10_dynamic_signals.log_firstHits.log"      # your daily log file
AVG_FILE = "instruments_avg_volume.csv"           # file containing avg volumes
OUTPUT_FILE = "coordinateRatio.csv"

# === Step 1: Read Log File ===
# use flexible whitespace separator

cols = ["Time", "Symbol", "Volume", "VolCutoff", "Criteria", "turnover", "Days", "UC"]

log_df = pd.read_csv(
    LOG_FILE,
    sep=r"(?<=\d{2}:\d{2}:\d{2})\s+|\s{2,}",          # regex: split on one or more whitespace
    engine="python",       # safer when using regex
    skipinitialspace=True,  # trim leading/trailing spaces
     skiprows=1, 
      names=cols,
)



# === Step 2: Read Average Volume File ===
avg_df = pd.read_csv(AVG_FILE)

# === Step 3: Join on Symbol/Tradingsymbol ===
merged = pd.merge(
    log_df,
    avg_df,
    left_on="Symbol",
    right_on="tradingsymbol",
    how="left"
)


merged["Volume"] = pd.to_numeric(merged["Volume"], errors="coerce")
merged["avg_volume"] = pd.to_numeric(merged["avg_volume"], errors="coerce")

# === Step 4: Compute Ratio ===
merged["volume_to_avg_ratio"] = merged["Volume"] / merged["avg_volume"]

# === Step 5: Optional — Round for readability ===
merged["volume_to_avg_ratio"] = merged["volume_to_avg_ratio"].round(2)
result = merged[["avg_volume", "Volume"]]
# === Step 6: Save to new file ===
result.to_csv(OUTPUT_FILE, index=False)

print(f"Saved merged results with ratios to {OUTPUT_FILE}")
