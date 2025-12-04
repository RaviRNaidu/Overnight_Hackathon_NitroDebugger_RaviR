# generate_dataset_10000.py
import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

# Output paths (change if you want)
SAVE_DIR = r"F:\hackathon"
os.makedirs(SAVE_DIR, exist_ok=True)
TRAIN_CSV = os.path.join(SAVE_DIR, "fertilizer_training_data_10000.csv")
REG_CSV = os.path.join(SAVE_DIR, "farmer_registry_10000.csv")

# -----------------------
# STATE -> MAJOR CROPS mapping
# (Curated from Govt. summaries & crop reports; main crops for each state)
# See citations after the script for sources used to choose crops.
# -----------------------
state_crops = {
    "Andhra Pradesh": ["Paddy", "Maize", "Groundnut"],
    "Arunachal Pradesh": ["Paddy", "Millet"],
    "Assam": ["Paddy", "Tea"],
    "Bihar": ["Paddy", "Maize", "Wheat"],
    "Chhattisgarh": ["Paddy", "Maize", "Soybean"],
    "Goa": ["Paddy", "Cashew"],
    "Gujarat": ["Groundnut", "Cotton", "Paddy"],
    "Haryana": ["Wheat", "Paddy", "Cotton"],
    "Himachal Pradesh": ["Apple", "Paddy", "Maize"],
    "Jharkhand": ["Paddy", "Maize", "Pulses"],
    "Karnataka": ["Ragi", "Maize", "Paddy", "Sugarcane"],
    "Kerala": ["Paddy", "Coconut", "Rubber"],
    "Madhya Pradesh": ["Wheat", "Soybean", "Maize"],
    "Maharashtra": ["Cotton", "Maize", "Sugarcane", "Soybean"],
    "Manipur": ["Paddy", "Maize"],
    "Meghalaya": ["Paddy", "Millet"],
    "Mizoram": ["Paddy", "Maize"],
    "Nagaland": ["Paddy", "Maize"],
    "Odisha": ["Paddy", "Groundnut"],
    "Punjab": ["Wheat", "Paddy"],
    "Rajasthan": ["Bajra", "Wheat", "Cotton"],
    "Sikkim": ["Paddy", "Potato"],
    "Tamil Nadu": ["Paddy", "Sugarcane", "Cotton"],
    "Telangana": ["Paddy", "Maize", "Cotton"],
    "Tripura": ["Paddy", "Maize"],
    "Uttar Pradesh": ["Wheat", "Paddy", "Sugarcane"],
    "Uttarakhand": ["Rice", "Wheat"],
    "West Bengal": ["Paddy", "Maize", "Jute"]
}

# -----------------------
# Crop baseline: recommended nutrient dose (kg/acre) and yield per hectare (kg/ha)
# These numbers are realistic approximations derived from government statistics (see citations).
# - recommended_dose: typical NPK/fertilizer kg per acre per season (approx)
# - yield_per_hectare: typical yield (kg/ha) used to compute crop-expected production
#
# Note: 1 hectare = 2.47105 acres. We store land in acres but yield is per hectare.
# -----------------------
crop_info = {
    "Paddy": {"dose_kg_per_acre": 50, "yield_kg_per_ha": 4000},
    "Wheat": {"dose_kg_per_acre": 45, "yield_kg_per_ha": 3500},
    "Maize": {"dose_kg_per_acre": 30, "yield_kg_per_ha": 3500},
    "Cotton": {"dose_kg_per_acre": 20, "yield_kg_per_ha": 700},  # cotton lint yield typical units differ
    "Groundnut": {"dose_kg_per_acre": 25, "yield_kg_per_ha": 1600},
    "Soybean": {"dose_kg_per_acre": 20, "yield_kg_per_ha": 1200},
    "Sugarcane": {"dose_kg_per_acre": 80, "yield_kg_per_ha": 70000}, # sugarcane yields are in t/ha, high
    "Ragi": {"dose_kg_per_acre": 15, "yield_kg_per_ha": 1000},
    "Millet": {"dose_kg_per_acre": 15, "yield_kg_per_ha": 900},
    "Pulses": {"dose_kg_per_acre": 10, "yield_kg_per_ha": 700},
    "Tea": {"dose_kg_per_acre": 10, "yield_kg_per_ha": 2500},
    "Cashew": {"dose_kg_per_acre": 5, "yield_kg_per_ha": 800},
    "Apple": {"dose_kg_per_acre": 5, "yield_kg_per_ha": 20000},
    "Coconut": {"dose_kg_per_acre": 10, "yield_kg_per_ha": 8000},
    "Rubber": {"dose_kg_per_acre": 10, "yield_kg_per_ha": 10000},
    "Bajra": {"dose_kg_per_acre": 12, "yield_kg_per_ha": 900},
    "Potato": {"dose_kg_per_acre": 40, "yield_kg_per_ha": 25000},
    "Jute": {"dose_kg_per_acre": 15, "yield_kg_per_ha": 1800}
}

# If a crop in mapping is not in crop_info, fallback to paddy-like values
default_info = {"dose_kg_per_acre": 30, "yield_kg_per_ha": 3000}

# -----------------------
# Helper lists and choices
# -----------------------
irrigation_types = ["Borewell", "Canal", "Rainfed"]
soil_types = ["Loam", "Clay", "Sandy"]
seasons = ["Kharif", "Rabi", "Zaid"]

# District names generator (synthetic, based on state)
def synth_district(state):
    # create a synthetic district name using the state short + random number
    short = "".join([w[0] for w in state.split() if w])
    return f"{state.split()[0]}Dist{random.randint(1,200)}"

# -----------------------
# Build datasets
# -----------------------
N = 10000
rows = []
registry = []

# create a pool of farmer IDs and Aadhaar-like numbers
farmer_ids = [f"F{str(i).zfill(6)}" for i in range(1, N+1)]
aadhaars = [str(100000000000 + i) for i in range(1, N+1)]

for i in range(N):
    # choose state weighted randomly (uniform across states)
    state = random.choice(list(state_crops.keys()))
    crop = random.choice(state_crops[state])
    crop_meta = crop_info.get(crop, default_info)
    dose = crop_meta["dose_kg_per_acre"]
    yield_per_ha = crop_meta["yield_kg_per_ha"]

    # land size realistic distribution: more smallholders, few large
    # we'll use a log-normal-ish sample scaled to 0.2 - 20 acres (but typical 0.5-5)
    land = round(float(np.clip(np.random.lognormal(mean=0.6, sigma=0.8), 0.2, 20.0)), 2)
    # choose season based on crop (approx): Paddy mostly Kharif, Wheat mostly Rabi
    if crop in ["Paddy"]:
        season = "Kharif"
    elif crop in ["Wheat", "Potato"]:
        season = "Rabi"
    else:
        season = random.choice(seasons)

    irrigation = random.choices(irrigation_types, weights=[0.4,0.2,0.4])[0]
    soil = random.choice(soil_types)

    # compute base allowed quantity using recommended dose (kg/acre * land)
    base_allowed = land * dose

    # add a realistic correction factor based on irrigation/soil/region
    # irrigation increases allowance slightly
    irrig_factor = 1.05 if irrigation in ["Borewell","Canal"] else 0.95
    soil_factor = 1.05 if soil == "Loam" else (0.95 if soil == "Sandy" else 1.0)
    region_factor = 1.0  # small random regional tweaks can be added later
    correction = random.uniform(0.92, 1.12)
    max_allowed_qty = round(base_allowed * irrig_factor * soil_factor * correction * region_factor, 2)

    # past usage roughly correlated to land * dose with noise
    past_usage = round(land * dose * random.uniform(0.6, 1.25), 2)

    # compute expected yield for the plot (using yield_per_ha, convert acres->ha)
    land_ha = land / 2.47105
    expected_yield = round(yield_per_ha * land_ha * random.uniform(0.85, 1.15), 2)

    # store record
    district = synth_district(state)
    tx = {
        "state": state,
        "district": district,
        "crop_type": crop,
        "season": season,
        "irrigation_type": irrigation,
        "soil_type": soil,
        "land_size_acres": land,
        "land_size_hectares": round(land_ha, 3),
        "recommended_dose_kg_per_acre": dose,
        "max_allowed_qty_kg": max_allowed_qty,
        "past_fertilizer_usage_kg": past_usage,
        "expected_yield_kg": expected_yield,
        "yield_per_ha_kg": yield_per_ha
    }
    rows.append(tx)

    # registry entry (one per farmer)
    registry.append({
        "aadhaar": aadhaars[i],
        "farmer_id": farmer_ids[i],
        "state": state,
        "district": district,
        "land_size_acres": land,
        "usual_crop": crop,
        "irrigation_type": irrigation,
        "soil_type": soil
    })

# Create DataFrames and save
df = pd.DataFrame(rows)
reg_df = pd.DataFrame(registry)

df.to_csv(TRAIN_CSV, index=False)
reg_df.to_csv(REG_CSV, index=False)

print("====================================================")
print("10000-row fertilizer training dataset created.")
print("Saved files:")
print(" -", TRAIN_CSV)
print(" -", REG_CSV)
print("====================================================")
