from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import pickle

app = Flask(__name__)

# ---------------- LOAD MODEL & SCALER ----------------
model  = pickle.load(open("kidney_model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))
print("✅ Model & Scaler loaded successfully")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        features = ["age", "bp", "sg", "al", "su", "bgr", "bu", "sc", "hemo"]
        values = {}
        for f in features:
            values[f] = float(request.form.get(f))

        input_data   = pd.DataFrame([[values[f] for f in features]],columns=features)
        input_scaled = scaler.transform(input_data)

        # ✅ FIX: proba[1] = CKD probability, proba[0] = healthy
        prediction          = model.predict(input_scaled)[0]
        proba               = model.predict_proba(input_scaled)[0]
        ckd_probability     = round(proba[1] * 100, 1)
        healthy_probability = round(proba[0] * 100, 1)
        is_ckd              = bool(prediction == 1)

        if ckd_probability >= 80:   risk_level = "High Risk"
        elif ckd_probability >= 50: risk_level = "Moderate Risk"
        elif ckd_probability >= 20: risk_level = "Low Risk"
        else:                       risk_level = "Very Low Risk"

        flags = []
        if values["bp"]   > 90:    flags.append("Elevated Blood Pressure")
        if values["al"]   > 0:     flags.append("Albumin Detected")
        if values["su"]   > 0:     flags.append("Sugar Detected")
        if values["bgr"]  > 140:   flags.append("High Blood Glucose")
        if values["bu"]   > 25:    flags.append("Elevated Blood Urea")
        if values["sc"]   > 1.2:   flags.append("Elevated Serum Creatinine")
        if values["hemo"] < 12:    flags.append("Low Hemoglobin (Anemia)")
        if values["sg"]   < 1.010: flags.append("Low Specific Gravity")

        return jsonify({
            "success":             True,
            "is_ckd":              is_ckd,
            "ckd_probability":     ckd_probability,
            "healthy_probability": healthy_probability,
            "risk_level":          risk_level,
            "flags":               flags,
            "values":              values,
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)