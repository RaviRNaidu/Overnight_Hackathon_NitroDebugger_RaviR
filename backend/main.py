# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import joblib
import numpy as np
import os
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

APP_DIR = os.path.dirname(__file__) or "."
REG_PATH = os.path.join(APP_DIR, "farmer_registry_10000.csv")
MODEL_PATH = os.path.join(APP_DIR, "max_qty_model.pkl")
TRANSACTIONS_CSV = os.path.join(APP_DIR, "transaction_log.csv")

app = FastAPI(title="Agri Subsidy - Max Qty Prediction API")

# allow all origins for hackathon/demo. For production, restrict origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Load registry ----------
if not os.path.exists(REG_PATH):
    print(f"Warning: registry file not found at {REG_PATH}")
    farmer_reg = pd.DataFrame(columns=[
        "aadhaar","farmer_id","state","district","land_size_acres",
        "usual_crop","irrigation_type","soil_type"
    ])
else:
    farmer_reg = pd.read_csv(REG_PATH, dtype={"aadhaar": str})

# ---------- Load ML model ----------
# Temporarily disabled due to sklearn version mismatch
# if not os.path.exists(MODEL_PATH):
#     raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Place max_qty_model.pkl here.")
# model_pipe = joblib.load(MODEL_PATH)
model_pipe = None  # Disabled temporarily

# ---------- Ensure transaction log exists ----------
if not os.path.exists(TRANSACTIONS_CSV):
    pd.DataFrame(columns=[
        "timestamp","transaction_id","aadhaar","farmer_id","state","district",
        "crop","requested_qty_kg","predicted_max_kg","rule_max_kg","approved"
    ]).to_csv(TRANSACTIONS_CSV, index=False)

# ---------- Helper functions ----------
def lookup_farmer(aadhaar: str):
    aad = str(aadhaar)
    rec = farmer_reg[farmer_reg['aadhaar'] == aad]
    if rec.empty:
        return None
    row = rec.iloc[0].to_dict()
    # ensure numeric land size
    row['land_size_acres'] = float(row.get('land_size_acres', 0.0))
    return row

def compute_rule_max(land_acres: float, crop: str, default_dose: float = None):
    """
    Simple rule: rule_max = land * recommended_dose
    recommended_dose chosen from pipe's training set if available, else default
    """
    # Try to infer recommended dose from pipeline training metadata if present
    # We don't have a direct map here; use simple fallback defaults
    dose_lookup = {
        "Paddy": 50, "Wheat":45, "Maize":30, "Cotton":20, "Groundnut":25,
        "Soybean":20, "Sugarcane":80, "Potato":40, "Ragi":15, "Millet":15
    }
    dose = dose_lookup.get(crop, default_dose if default_dose is not None else 30)
    return round(land_acres * dose, 2)

def build_feature_row(farmer_row: dict):
    """
    Build a single-row (dict) matching the pipeline features used in training.
    Must match cat_features & num_features order used in Colab.
    """
    # expected keys in registry: state, crop usual_crop (means same), season guess, irrigation_type, soil_type
    state = farmer_row.get("state", "")
    crop_type = farmer_row.get("usual_crop", farmer_row.get("crop", "Paddy"))
    irrigation = farmer_row.get("irrigation_type", "Rainfed")
    soil = farmer_row.get("soil_type", "Loam")
    land = float(farmer_row.get("land_size_acres", 0.0))

    # derive engineered features similar to training
    recommended = None
    # a small default mapping - matches dataset generator
    dose_map = {"Paddy":50,"Wheat":45,"Maize":30,"Cotton":20,"Groundnut":25,"Soybean":20,"Sugarcane":80}
    recommended = dose_map.get(crop_type, 30)

    base_qty = land * recommended
    # past_usage is not in registry for simple mock; assume base*0.9
    past_usage_per_acre = (base_qty * 0.9) / (land if land>0 else 1.0)
    yield_per_acre = 0.0  # optional; model tolerates zeros
    land_sq = land**2

    # season heuristic
    if crop_type == "Paddy":
        season = "Kharif"
    elif crop_type in ["Wheat","Potato","Barley"]:
        season = "Rabi"
    else:
        season = "Kharif"

    # build dict that matches columns order (cat features first as in Colab)
    row = {
        "state": state,
        "crop_type": crop_type,
        "season": season,
        "irrigation_type": irrigation,
        "soil_type": soil,
        "land_size_acres": land,
        "recommended_dose_kg_per_acre": recommended,
        "past_usage_per_acre": past_usage_per_acre,
        "base_qty": base_qty,
        "yield_per_acre": yield_per_acre,
        "land_sq": land_sq
    }
    return row

# ---------- API schemas ----------
class PredictRequest(BaseModel):
    aadhaar: Optional[str] = None
    # optional override fields (allows predicting for not-in-registry farmers)
    state: Optional[str] = None
    crop_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    soil_type: Optional[str] = None
    land_size_acres: Optional[float] = None

class SubmitRequest(BaseModel):
    aadhaar: str
    requested_qty_kg: float

# ---------- Endpoints ----------
@app.get("/")
def root():
    return {"status":"ok","message":"Agri Subsidy Prediction API"}

@app.post("/get_farmer/")
def get_farmer(aadhaar: str):
    rec = lookup_farmer(aadhaar)
    if rec is None:
        raise HTTPException(status_code=404, detail="Aadhaar not found in registry.")
    return rec

@app.post("/predict_max_qty/")
def predict_max(req: PredictRequest):
    # Try registry if aadhaar provided
    if req.aadhaar:
        reg = lookup_farmer(req.aadhaar)
        if reg is None:
            # allow prediction using provided override fields
            if not (req.state and req.crop_type and req.land_size_acres):
                raise HTTPException(status_code=404, detail="Aadhaar not found; provide state, crop_type, land_size_acres to predict.")
            farmer_row = {
                "state": req.state,
                "usual_crop": req.crop_type,
                "irrigation_type": req.irrigation_type or "Rainfed",
                "soil_type": req.soil_type or "Loam",
                "land_size_acres": req.land_size_acres
            }
        else:
            farmer_row = reg
    else:
        # Aadhaar not provided; require overrides
        if not (req.state and req.crop_type and req.land_size_acres):
            raise HTTPException(status_code=400, detail="Provide aadhaar or (state, crop_type, land_size_acres).")
        farmer_row = {
            "state": req.state,
            "usual_crop": req.crop_type,
            "irrigation_type": req.irrigation_type or "Rainfed",
            "soil_type": req.soil_type or "Loam",
            "land_size_acres": req.land_size_acres
        }

    # Build feature vector and predict
    feat = build_feature_row(farmer_row)
    X_df = pd.DataFrame([feat])
    
    # Use model if available, otherwise use rule-based calculation
    if model_pipe is not None:
        pred = float(model_pipe.predict(X_df)[0])
    else:
        # Fallback to rule-based calculation when model is unavailable
        rule_max = compute_rule_max(feat['land_size_acres'], feat['crop_type'])
        pred = rule_max

    # Compute rule-based max and clamp predicted value within a safe bound
    rule_max = compute_rule_max(feat['land_size_acres'], feat['crop_type'])
    # clamp to [0, rule_max * 1.15] (15% buffer)
    upper_bound = max(rule_max * 1.15, 0.0)
    lower_bound = 0.0
    pred_clamped = round(float(np.clip(pred, lower_bound, upper_bound)), 2)

    return {
        "predicted_max_qty_kg": round(pred,2),
        "predicted_max_qty_kg_clamped": pred_clamped,
        "rule_max_qty_kg": rule_max,
        "upper_bound_kg": round(upper_bound,2),
        "input_features": feat
    }

@app.post("/submit_request/")
def submit_request(body: SubmitRequest):
    # Validate
    reg = lookup_farmer(body.aadhaar)
    if reg is None:
        raise HTTPException(status_code=404, detail="Aadhaar not found; cannot submit.")
    feat = build_feature_row(reg)
    X_df = pd.DataFrame([feat])
    
    # Use model if available, otherwise use rule-based calculation
    if model_pipe is not None:
        pred = float(model_pipe.predict(X_df)[0])
    else:
        # Fallback to rule-based calculation when model is unavailable
        rule_max = compute_rule_max(reg.get("land_size_acres", 2.0), body.crop)
        pred = rule_max
    rule_max = compute_rule_max(feat['land_size_acres'], feat['crop_type'])
    upper_bound = max(rule_max * 1.15, 0.0)
    approved = False
    if 0 <= body.requested_qty_kg <= upper_bound:
        approved = True

    # Log transaction
    tx = {
        "timestamp": datetime.utcnow().isoformat(),
        "transaction_id": f"T{int(pd.Timestamp.utcnow().timestamp())}",
        "aadhaar": body.aadhaar,
        "farmer_id": reg.get("farmer_id","UNKNOWN"),
        "state": reg.get("state"),
        "district": reg.get("district"),
        "crop": reg.get("usual_crop"),
        "requested_qty_kg": body.requested_qty_kg,
        "predicted_max_kg": round(pred,2),
        "rule_max_kg": rule_max,
        "approved": approved
    }
    # Append to CSV
    tx_df = pd.DataFrame([tx])
    existing = pd.read_csv(TRANSACTIONS_CSV)
    concat = pd.concat([existing, tx_df], ignore_index=True)
    concat.to_csv(TRANSACTIONS_CSV, index=False)

    return {"approved": approved, "transaction": tx}
