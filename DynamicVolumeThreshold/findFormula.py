import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import matplotlib.ticker as mtick

# ==== STEP 1: Your Data Points ====
# avg_volume (X) and min_required_volume (Y)
X = np.array([50000,100000,150000,300000,500000,800000,1000000,2000000,5000000,10000000,15000000,25000000,40000000])
Y = np.array([50000*0.40,100000*0.38,150000*0.32,300000*0.28,500000*0.25,800000*0.23,1000000*0.20,2000000*0.18,5000000*0.15,10000000*0.10,15000000*0.07,25000000*0.05,40000000*0.04])

# ==== STEP 2: Define Candidate Models ====
def log_func(x, a, b):
    return a * np.log(x) + b

def power_func(x, a, b):
    return a * np.power(x, b)

# ==== STEP 3: Fit Both Models ====
popt_log, _ = curve_fit(log_func, X, Y, maxfev=5000)
popt_power, _ = curve_fit(power_func, X, Y, maxfev=5000)

# ==== STEP 4: Plot ====
x_range = np.linspace(min(X), max(X), 200)

plt.scatter(X, Y, color="red", label="Your Points")
plt.plot(x_range, log_func(x_range, *popt_log), label=f"Log Fit: y = {popt_log[0]:.2f}*ln(x) + {popt_log[1]:.2f}")
plt.plot(x_range, power_func(x_range, *popt_power), label=f"Power Fit: y = {popt_power[0]:.2e}*x^{popt_power[1]:.2f}")

plt.xlabel("Average Volume")
plt.ylabel("Min Required Volume")
plt.gca().xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M'))
plt.legend()
plt.show()

print("\n--- Best Fit Formulas ---")
print(f"Logarithmic Fit: y = {popt_log[0]:.2f} * ln(x) + {popt_log[1]:.2f}")
print(f"Power Fit: y = {popt_power[0]:.2e} * x^{popt_power[1]:.2f}")


# Logarithmic Fit: y = 185364.90 * ln(x) + -2121427.08
#Power Fit: y = 2.08e+01 * x^0.65