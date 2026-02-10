def volume_threshold(avg_vol, a=2.08e+01, b=0.65):
    threshold = a * (avg_vol ** b)
    return round(threshold,0)

print(volume_threshold(1143153))