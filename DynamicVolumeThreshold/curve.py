# train_threshold_curve.py
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

# -------------------------
# USER: replace with your CSV or inline arrays
# Data must contain: avg_volume, current_volume, label (1/0)
# Example small dataset -- replace with your real CSV load
# -------------------------
# Example synthetic data loader (replace)
df = pd.read_csv("training.csv")  # expected columns avg_volume,current_volume,label
X_raw = df["avg_volume"].values
Y_raw = df["current_volume"].values
labels = df["label"].astype(int).values

# # For demo, create small example arrays (you will replace these)
# X_raw = np.array([50000,100000,150000,300000,500000,800000,1000000,2000000,5000000,10000000], dtype=float)
# Y_raw = np.array([28000,51500,75000,145000,225000,335000,380000,500000,800000,1000000], dtype=float)
# labels = np.array([1,1,1,1,1,1,1,1,1,1], dtype=int)  # replace with your supervised labels

# ---------- USER SETTINGS ----------
# loss weights (alpha for missing true points; beta for false positives)
alpha = 1.0
beta = 2.0    # customer requested 2:1 preference

# regularization strengths (tweakable)
lambda_smooth = 1.0
lambda_mono   = 10.0

# training params
lr = 1e-3
epochs = 3000
patience = 200
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # you said local CPU, adjust to "cuda" if GPU available

# whether to log-transform X (recommended)
use_logX = True

# -------------------------
# Prepare tensors
# -------------------------
def prepare(X_raw, Y_raw, labels, use_logX=True):
    X = np.log1p(X_raw) if use_logX else X_raw.copy()
    X = X.astype(np.float32).reshape(-1, 1)
    Y = Y_raw.astype(np.float32).reshape(-1, 1)
    L = labels.astype(np.float32).reshape(-1, 1)
    return torch.tensor(X), torch.tensor(Y), torch.tensor(L)

X_t, Y_t, L_t = prepare(X_raw, Y_raw, labels, use_logX=use_logX)

# Train/val split (small data; preserve same distribution)
X_train, X_val, Y_train, Y_val, L_train, L_val = train_test_split(
    X_t.numpy(), Y_t.numpy(), L_t.numpy(), test_size=0.2, random_state=42
)
X_train = torch.tensor(X_train, dtype=torch.float32)
Y_train = torch.tensor(Y_train, dtype=torch.float32)
L_train = torch.tensor(L_train, dtype=torch.float32)
X_val = torch.tensor(X_val, dtype=torch.float32)
Y_val = torch.tensor(Y_val, dtype=torch.float32)
L_val = torch.tensor(L_val, dtype=torch.float32)

# -------------------------
# Model
# -------------------------
class MLP(nn.Module):
    def __init__(self, hidden=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(1, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, 1)
        )
    def forward(self, x):
        return self.net(x)

model = MLP(hidden=64).to(device)
opt = optim.Adam(model.parameters(), lr=lr)

# Precompute a sorted unique grid for monotonicity + smoothness penalties
# We'll use a dense grid of X values spanning the observed avg_volume range
if use_logX:
    x_grid_raw = np.linspace(np.min(np.log1p(X_raw)), np.max(np.log1p(X_raw)), 200)
else:
    x_grid_raw = np.linspace(np.min(X_raw), np.max(X_raw), 200)
x_grid = torch.tensor(x_grid_raw, dtype=torch.float32).unsqueeze(1).to(device)

# -------------------------
# Training loop with custom loss
# -------------------------
best_val = float("inf")
best_state = None
no_improve = 0

for epoch in range(epochs):
    model.train()
    opt.zero_grad()

    preds = model(X_train.to(device))                       # shape (n,1)
    # hinge-like asymmetric loss (ReLU)
    loss_pos = torch.relu(preds - Y_train.to(device)) * L_train.to(device) * alpha   # bad if pred > y for true points
    loss_neg = torch.relu(Y_train.to(device) - preds) * (1 - L_train.to(device)) * beta  # bad if pred < y for false points
    loss_main = (loss_pos + loss_neg).mean()

    # monotonicity penalty: penalize negative diffs across grid
    with torch.no_grad():
        # evaluate preds on grid for monotonicity and smoothness
        pass
    preds_grid = model(x_grid)   # shape (grid,1)
    diffs = preds_grid[1:] - preds_grid[:-1]          # first differences
    mono_pen = torch.relu(-diffs).mean()              # penalize negative steps
    # smoothness: second difference squared
    smooth_pen = (diffs[1:] - diffs[:-1]).pow(2).mean()

    loss = loss_main + lambda_mono * mono_pen + lambda_smooth * smooth_pen
    loss.backward()
    opt.step()

    # validation loss (no grad)
    model.eval()
    with torch.no_grad():
        preds_val = model(X_val.to(device))
        val_pos = torch.relu(preds_val - Y_val.to(device)) * L_val.to(device) * alpha
        val_neg = torch.relu(Y_val.to(device) - preds_val) * (1 - L_val.to(device)) * beta
        val_main = (val_pos + val_neg).mean()

        preds_grid_val = model(x_grid)
        diffs_val = preds_grid_val[1:] - preds_grid_val[:-1]
        mono_val = torch.relu(-diffs_val).mean()
        smooth_val = (diffs_val[1:] - diffs_val[:-1]).pow(2).mean()

        val_loss = val_main + lambda_mono * mono_val + lambda_smooth * smooth_val

    if val_loss.item() < best_val - 1e-8:
        best_val = val_loss.item()
        best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        no_improve = 0
    else:
        no_improve += 1

    if epoch % 200 == 0 or epoch == epochs-1:
        print(f"epoch {epoch:04d} train_loss={loss.item():.6f} val_loss={val_loss.item():.6f} mono={mono_val.item():.6f} smooth={smooth_val.item():.6f}")

    if no_improve > patience:
        print("Early stopping.")
        break

# load best
if best_state is not None:
    model.load_state_dict(best_state)

# -------------------------
# Evaluate on full dataset
# -------------------------
model.eval()
with torch.no_grad():
    X_all = torch.tensor(np.log1p(X_raw) if use_logX else X_raw, dtype=torch.float32).unsqueeze(1)
    preds_all = model(X_all).squeeze().numpy()       # learned curve values (predicted_threshold)
    # compute predicted labels on your training points:
    pred_labels = (Y_raw >= preds_all).astype(int)
    tp = np.sum((pred_labels == 1) & (labels == 1))
    fn = np.sum((pred_labels == 0) & (labels == 1))
    fp = np.sum((pred_labels == 1) & (labels == 0))
    tn = np.sum((pred_labels == 0) & (labels == 0))
    print("TP, FN, FP, TN:", tp, fn, fp, tn)
    tpr = tp / max(1, (tp+fn))
    fpr = fp / max(1, (fp+tn))
    print(f"TPR={tpr:.3f} FPR={fpr:.3f} SuccessRate={np.mean((labels==1) & (Y_raw>=preds_all)):.3f}")

# -------------------------
# Fit parametric forms to the learned curve
# -------------------------
# We'll fit both: log form (a*ln(x)+b) and power form (a*x^b)
x_for_fit = X_raw.copy()
y_for_fit = preds_all.copy()

# Remove any non-finite values
mask = np.isfinite(x_for_fit) & np.isfinite(y_for_fit) & (x_for_fit > 0)
x_fit = x_for_fit[mask]
y_fit = y_for_fit[mask]

def log_func(x, a, b):
    return a * np.log(x) + b

def power_func(x, a, b):
    return a * (x ** b)

# Use curve_fit with bounds to help stability
popt_log, _ = curve_fit(log_func, x_fit, y_fit, maxfev=5000)
popt_power, _ = curve_fit(power_func, x_fit, y_fit, maxfev=5000)

# Compute R^2 for both fits
def r2(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred)**2)
    ss_tot = np.sum((y_true - np.mean(y_true))**2)
    return 1 - ss_res / (ss_tot + 1e-12)

y_log_pred = log_func(x_fit, *popt_log)
y_power_pred = power_func(x_fit, *popt_power)
print("\nParametric fits:")
print(f"Log fit: y = {popt_log[0]:.6f} * ln(x) + {popt_log[1]:.6f}  R2={r2(y_fit, y_log_pred):.4f}")
print(f"Power fit: y = {popt_power[0]:.6e} * x^{popt_power[1]:.6f}  R2={r2(y_fit, y_power_pred):.4f}")

# -------------------------
# Plot results
# -------------------------
plt.figure(figsize=(9,6))
# scatter raw points (color by label)
c = ['red' if lab==0 else 'green' for lab in labels]
plt.scatter(X_raw, Y_raw, c=c, alpha=0.9, label='points (green=good)')
# NN learned curve on a dense grid
x_dense = np.linspace(np.min(X_raw), np.max(X_raw), 300)
x_dense_transform = np.log1p(x_dense) if use_logX else x_dense
with torch.no_grad():
    preds_dense = model(torch.tensor(x_dense_transform, dtype=torch.float32).unsqueeze(1)).squeeze().numpy()
plt.plot(x_dense, preds_dense, color='blue', label='NN learned curve', linewidth=2)
# parametric fits
plt.plot(x_dense, log_func(x_dense, *popt_log), color='orange', linestyle='--', label='log fit')
plt.plot(x_dense, power_func(x_dense, *popt_power), color='purple', linestyle=':', label='power fit')

plt.xscale('log')   # optional log-scale x for readability
plt.xlabel('Average volume (X)')
plt.ylabel('Threshold volume (Y_expected)')
plt.legend()
plt.grid(True)
plt.title('Learned threshold curve and parametric fits')
plt.show()

# -------------------------
# Print final chosen formula to use in production
# -------------------------
print("\nChoose a production formula (copy-paste):")
print(f"Log fit: y = {popt_log[0]:.6f} * ln(x) + {popt_log[1]:.6f}")
print(f"Power fit: y = {popt_power[0]:.6e} * x^{popt_power[1]:.6f}")

# small utility you can copy into your scanner
print("\nExample function to use in scanner:")
print("def dynamic_cutoff_log(avg_volume):")
print(f"    return {popt_log[0]:.6f} * math.log(avg_volume) + {popt_log[1]:.6f}")

print("\nOr power form:")
print("def dynamic_cutoff_power(avg_volume):")
print(f"    return {popt_power[0]:.6e} * (avg_volume ** {popt_power[1]:.6f})")
