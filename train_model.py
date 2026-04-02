# train_model.py — FIXED VERSION
# Bug: LabelEncoder gave ckd=0, notckd=1 (alphabetical)
# Fix: Explicit map ckd=1, notckd=0

import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# ---------------- LOAD DATA ----------------
df = pd.read_csv("Kidney-Dataset(CKD).csv")

FEATURES = ["age", "bp", "sg", "al", "su", "bgr", "bu", "sc", "hemo"]
TARGET   = "classification"

df = df[FEATURES + [TARGET]].copy()

# Strip tabs/spaces (dataset has 'ckd\t' entries)
df[TARGET] = df[TARGET].str.strip()

# ✅ FIX: Explicit encoding — ckd=1, notckd=0
df[TARGET] = df[TARGET].map({'ckd': 1, 'notckd': 0})

# ---------------- HANDLE MISSING VALUES ----------------
for col in FEATURES:
    df[col] = pd.to_numeric(df[col].replace("?", np.nan), errors='coerce')
    df[col] = df[col].fillna(df[col].mean())

# ---------------- SPLIT ----------------
X = df[FEATURES]
y = df[TARGET]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ---------------- SCALE ----------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# ---------------- TRAIN ----------------
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train_scaled, y_train)

# ---------------- EVALUATE ----------------
y_pred = model.predict(X_test_scaled)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred, target_names=['notckd', 'ckd']))

# Sanity check
ckd_case     = np.array([[65, 90, 1.005, 4, 3, 380, 150, 7.2, 7.5]])
healthy_case = np.array([[30, 70, 1.025,  0, 0,  90,  20, 0.8, 15.5]])
print(f"CKD case     → {model.predict(scaler.transform(ckd_case))[0]}  (expected 1)")
print(f"Healthy case → {model.predict(scaler.transform(healthy_case))[0]}  (expected 0)")

# ---------------- SAVE ----------------
pickle.dump(model,  open("kidney_model.pkl", "wb"))
pickle.dump(scaler, open("scaler.pkl",       "wb"))
print("✅ Model & Scaler saved!")