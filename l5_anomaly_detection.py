# ============================================================
# ESZG517 — Lab Session L5: Anomaly Detection
# Run this in Google Colab or locally with the dependencies below.
# pip install numpy pandas matplotlib scikit-learn
# ============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

N_NORMAL = 200
N_ANOMALY = 10

# ── Simulate 200 normal readings for each sensor ──────────────────────────────
timestamps = pd.date_range("2025-01-01", periods=N_NORMAL, freq="5min")

temperature = np.random.normal(loc=22.0, scale=1.5, size=N_NORMAL)   # °C
humidity    = np.random.normal(loc=55.0, scale=5.0, size=N_NORMAL)   # %
motion      = np.random.binomial(n=1, p=0.2, size=N_NORMAL)          # 0 or 1
light       = np.random.normal(loc=300.0, scale=30.0, size=N_NORMAL) # lux

# ── Inject anomalies at random positions ──────────────────────────────────────
anomaly_idx = np.random.choice(N_NORMAL, N_ANOMALY, replace=False)

temperature[anomaly_idx[:3]]  += np.random.uniform(10, 15, 3)   # spike high
humidity[anomaly_idx[3:6]]    -= np.random.uniform(30, 40, 3)   # drop low
motion[anomaly_idx[6:8]]       = 1                              # unexpected motion
light[anomaly_idx[8:]]        += np.random.uniform(400, 600, 2) # overexposure

df = pd.DataFrame({
    "timestamp":   timestamps,
    "temperature": temperature,
    "humidity":    humidity,
    "motion":      motion,
    "light":       light,
})

# ── Isolation Forest anomaly detection ────────────────────────────────────────
sensors = ["temperature", "humidity", "motion", "light"]
df["anomaly"] = 0

for sensor in sensors:
    model = IsolationForest(contamination=0.05, random_state=RANDOM_SEED)
    preds = model.fit_predict(df[[sensor]])
    # IsolationForest labels anomalies as -1
    df.loc[preds == -1, "anomaly"] = 1

print(f"Total anomalies detected: {df['anomaly'].sum()}")
print(df[df["anomaly"] == 1][["timestamp"] + sensors])

# ── Plot: four subplots with red anomaly dots ──────────────────────────────────
fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)
fig.suptitle("L5 — Smart Home Sensor Anomaly Detection", fontsize=14, fontweight="bold")

colors   = ["steelblue", "darkorange", "seagreen", "mediumpurple"]
y_labels = ["Temperature (°C)", "Humidity (%)", "Motion (0/1)", "Light (lux)"]
units    = sensors

for ax, sensor, color, ylabel in zip(axes, sensors, colors, y_labels):
    normal_mask  = df["anomaly"] == 0
    anomaly_mask = df["anomaly"] == 1

    ax.plot(df.loc[normal_mask,  "timestamp"], df.loc[normal_mask,  sensor],
            color=color, linewidth=0.9, label="Normal")
    ax.scatter(df.loc[anomaly_mask, "timestamp"], df.loc[anomaly_mask, sensor],
               color="red", zorder=5, s=60, label="Anomaly")
    ax.set_ylabel(ylabel)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, linestyle="--", alpha=0.4)

axes[-1].set_xlabel("Timestamp")
plt.tight_layout()
plt.savefig("l5_anomaly_graph.png", dpi=150, bbox_inches="tight")
print("Saved: l5_anomaly_graph.png")
plt.show()
