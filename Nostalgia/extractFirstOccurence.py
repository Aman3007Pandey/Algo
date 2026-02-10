from datetime import datetime

# LOG_FILE = f"{datetime.now().strftime('%Y-%m-%d')}_momentum_signals.log.log"
# LOG_FILE = "2025-10-15_momentum_signals.log.log"
# LOG_FILE = "2025-10-10_dynamic_signals.log"
LOG_FILE="2025-10-23_volume_signals.log"
FIRST_HIT_SUFFIX = "firstHits"

seen = set()
output_lines = []

with open(LOG_FILE, "r") as f:
    header = f.readline()
    output_lines.append(header)  # keep header
    for line in f:
        parts = line.split()
        if len(parts) < 3:
            continue
        symbol = parts[2]
        print(symbol)
        if symbol not in seen:
            seen.add(symbol)
            output_lines.append(line)

out_file = f"{LOG_FILE}_{FIRST_HIT_SUFFIX}.log"
with open(out_file, "w") as f:
    f.writelines(output_lines)

print(f"✅ Saved {len(output_lines)-1} first-hit rows to {out_file}")
