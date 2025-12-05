"""
Agricultural Subsidy Fraud Detection - Real-time Predictor
Simplified version with clear decision logic
"""

import joblib
import pandas as pd
import numpy as np
from haversine import haversine
import json

print("Loading models and reference data...")

isolation_model = joblib.load("models/isolation_forest.pkl")
try:
    xgb_model = joblib.load("models/xgboost_model.pkl")
    use_xgb = True
    print("XGBoost model loaded.")
except:
    use_xgb = False
    print("XGBoost model not found.")

scaler = joblib.load("models/feature_scaler.pkl")

farmers = pd.read_csv("farmers.csv")
dealers = pd.read_csv("dealers.csv")
scheme = pd.read_csv("scheme_rules.csv")
transactions = pd.read_csv("transactions.csv")

print("Loaded all reference data.\n")

# Load transaction from JSON
with open("sample_txn.json", "r") as f:
    sample_input = json.load(f)

print("Incoming Transaction (from JSON):")
for k, v in sample_input.items():
    print(f"  {k}: {v}")

# SEASONAL PRODUCT RECOMMENDATIONS BASED ON DATE
print("\n--- Seasonal Product Recommendation ---")
try:
    txn_date = pd.to_datetime(sample_input["txn_date"])
    month = txn_date.month
    
    # Define seasons with recommended products AND crops
    seasons = {
        "Rabi (Oct-Mar)": {
            "months": [10, 11, 12, 1, 2, 3],
            "products": ["Urea", "DAP", "Seeds", "Pesticide"],
            "crops": ["Wheat", "Paddy", "Pulses"]
        },
        "Kharif (Jun-Sep)": {
            "months": [6, 7, 8, 9],
            "products": ["Urea", "DAP", "MOP", "Seeds", "Pesticide"],
            "crops": ["Maize", "Cotton", "Sugarcane"]
        },
        "Summer (Apr-May)": {
            "months": [4, 5],
            "products": ["Seeds", "Machinery", "Pesticide"],
            "crops": ["Vegetables"]
        }
    }
    
    current_season = None
    recommended_products = []
    recommended_crops = []
    
    for season_name, season_data in seasons.items():
        if month in season_data["months"]:
            current_season = season_name
            recommended_products = season_data["products"]
            recommended_crops = season_data["crops"]
            break
    
    print(f"Transaction Date: {txn_date.strftime('%Y-%m-%d')}")
    print(f"Current Season: {current_season}")
    print(f"Recommended Products: {', '.join(recommended_products)}")
    print(f"Typical Crops: {', '.join(recommended_crops)}")
    
    # Check if selected product/crop matches season
    product_type = sample_input.get("product_type", None)
    crop_type = sample_input.get("crop_type", None)
    
    if product_type and product_type in recommended_products:
        print(f"OK {product_type} is APPROPRIATE for {current_season}")
    elif product_type and product_type not in recommended_products:
        print(f"! {product_type} is NOT typical for {current_season}")
    
    if crop_type:
        if crop_type in recommended_crops:
            print(f"OK {crop_type} is APPROPRIATE crop for {current_season}")
        else:
            print(f"! {crop_type} is NOT typical crop for {current_season}")
            print(f"  Consider: {', '.join(recommended_crops)}")
        
except Exception as e:
    print(f"Could not determine season: {e}")

# Fetch farmer, dealer, and scheme info
f = farmers[farmers.farmer_id == sample_input["farmer_id"]].head(1)
d = dealers[dealers.dealer_id == sample_input["dealer_id"]].head(1)

# GHOST FARMER DETECTION
print("\n--- Farmer & Dealer Validation ---")
is_ghost_farmer = f.empty
if is_ghost_farmer:
    print(f"WARNING: Farmer {sample_input['farmer_id']} NOT FOUND in master list")
    print("         This is a RED FLAG for fraud detection")

product_type = sample_input.get("product_type", None)
crop_type = sample_input.get("crop_type", None)

# Determine which one to use for scheme lookup (product_type takes priority)
lookup_product = product_type if product_type else None

if lookup_product:
    s = scheme[(scheme.product_type == lookup_product) & 
               (scheme.season == "Rabi")].head(1)
    if s.empty:
        s = scheme[(scheme.product_type == lookup_product)].head(1)
else:
    # If no product_type provided, try to find scheme for any product applicable to crop
    s = pd.DataFrame()
    if crop_type:
        s = scheme[scheme.applicable_crops.str.contains(crop_type, na=False)].head(1)

# Get scheme limits for auto-calculation
max_qty_per_ha = float(s.max_qty_per_ha.iloc[0]) if not s.empty else 0
max_subsidy = float(s.max_subsidy_amount.iloc[0]) if not s.empty else 0

# Handle AUTO-CALCULATED values
quantity_kg = sample_input.get("quantity_kg")
subsidy_amount = sample_input.get("subsidy_amount")

if quantity_kg == "AUTO":
    claimed_land = sample_input.get("claimed_land_area_ha", 2.0)
    quantity_kg = max_qty_per_ha * claimed_land
    print(f"\n[AUTO] Quantity: {quantity_kg:.2f} kg ({max_qty_per_ha} kg/ha x {claimed_land} ha)")

if subsidy_amount == "AUTO":
    subsidy_amount = max_subsidy * 0.55
    print(f"[AUTO] Subsidy: Rs {subsidy_amount:.2f} (55% of max)")

# Convert to float
quantity_kg = float(quantity_kg) if quantity_kg != "AUTO" else 0
subsidy_amount = float(subsidy_amount) if subsidy_amount != "AUTO" else 0

print("\n--- Computing All 32 Features ---")

feature_dict = {}

feature_dict['quantity_kg'] = quantity_kg
feature_dict['subsidy_amount'] = subsidy_amount
feature_dict['geo_lat'] = sample_input.get("geo_lat", 0)
feature_dict['geo_lon'] = sample_input.get("geo_lon", 0)
feature_dict['claimed_land_area_ha'] = sample_input.get("claimed_land_area_ha", 0)
feature_dict['amount_paid_by_farmer'] = sample_input.get("amount_paid_by_farmer", 0)

land = float(f.land_holding_ha.iloc[0]) if not f.empty else 0
feature_dict['land_holding_ha'] = land
print(f"1. Farmer Land Holding: {land} ha")

dealer_lat = float(d.lat.iloc[0]) if not d.empty else np.nan
dealer_lon = float(d.lon.iloc[0]) if not d.empty else np.nan
feature_dict['lat'] = dealer_lat
feature_dict['lon'] = dealer_lon

num_outlets = float(d.num_outlets.iloc[0]) if not d.empty else np.nan
feature_dict['num_outlets'] = num_outlets
print(f"2. Dealer Outlets: {num_outlets}")

avg_monthly_txn = float(d.avg_monthly_txn.iloc[0]) if not d.empty else np.nan
feature_dict['avg_monthly_txn'] = avg_monthly_txn
print(f"3. Dealer Avg Monthly Txn: {avg_monthly_txn}")

inventory_received = float(d.inventory_received_kg.iloc[0]) if not d.empty else np.nan
feature_dict['inventory_received_kg'] = inventory_received
print(f"4. Dealer Inventory Received: {inventory_received} kg")

suspicious_dealer = float(d.suspicious_dealer.iloc[0]) if not d.empty else 0
feature_dict['suspicious_dealer'] = suspicious_dealer
print(f"5. Suspicious Dealer Flag: {suspicious_dealer}")

feature_dict['max_qty_per_ha'] = max_qty_per_ha
print(f"6. Max Quantity Per Ha (from scheme): {max_qty_per_ha}")

feature_dict['max_subsidy_amount'] = max_subsidy
print(f"7. Max Subsidy Amount (from scheme): {max_subsidy}")

eligibility_min = float(s.eligibility_land_min.iloc[0]) if not s.empty else 0
feature_dict['eligibility_land_min'] = eligibility_min
print(f"8. Eligibility Land Min: {eligibility_min} ha")

eligibility_max = float(s.eligibility_land_max.iloc[0]) if not s.empty else np.nan
feature_dict['eligibility_land_max'] = eligibility_max
print(f"9. Eligibility Land Max: {eligibility_max} ha")

quantity_per_hectare = quantity_kg / max(feature_dict['claimed_land_area_ha'], 0.1)
feature_dict['quantity_per_hectare'] = quantity_per_hectare
print(f"10. Quantity Per Hectare: {quantity_per_hectare:.2f}")

land_vs_claim = feature_dict['claimed_land_area_ha'] - land
feature_dict['land_vs_claim_diff'] = land_vs_claim
print(f"11. Land vs Claimed Diff: {land_vs_claim:.2f} ha")

farmer_txn_count = len(transactions[transactions.farmer_id == sample_input["farmer_id"]])
feature_dict['farmer_total_transactions'] = farmer_txn_count
print(f"12. Farmer Total Transactions: {farmer_txn_count}")

farmer_qty_total = transactions[transactions.farmer_id == sample_input["farmer_id"]]['quantity_kg'].sum()
feature_dict['farmer_total_quantity'] = farmer_qty_total
print(f"13. Farmer Total Quantity: {farmer_qty_total:.2f} kg")

dealer_unique_farmers = transactions[transactions.dealer_id == sample_input["dealer_id"]]['farmer_id'].nunique()
feature_dict['dealer_total_farmers'] = dealer_unique_farmers
print(f"14. Dealer Unique Farmers: {dealer_unique_farmers}")

dealer_txn_count = len(transactions[transactions.dealer_id == sample_input["dealer_id"]])
feature_dict['dealer_total_transactions'] = dealer_txn_count
print(f"15. Dealer Total Transactions: {dealer_txn_count}")

dealer_qty_total = transactions[transactions.dealer_id == sample_input["dealer_id"]]['quantity_kg'].sum()
feature_dict['dealer_total_quantity'] = dealer_qty_total
print(f"16. Dealer Total Quantity: {dealer_qty_total:.2f} kg")

invoice_dup = len(transactions[(transactions.dealer_id == sample_input["dealer_id"]) & 
                               (transactions.invoice_no == sample_input["invoice_no"])]) > 1
feature_dict['invoice_duplicate_flag'] = 1 if invoice_dup else 0
print(f"17. Invoice Duplicate Flag: {feature_dict['invoice_duplicate_flag']}")

allowed_quantity = max_qty_per_ha * land
feature_dict['allowed_quantity'] = allowed_quantity
print(f"18. Allowed Quantity: {allowed_quantity:.2f} kg")

quantity_vs_allowed = quantity_kg - allowed_quantity
feature_dict['quantity_vs_allowed'] = quantity_vs_allowed
print(f"19. Quantity vs Allowed: {quantity_vs_allowed:.2f} kg")

subsidy_vs_allowed = subsidy_amount - max_subsidy
feature_dict['subsidy_vs_allowed'] = subsidy_vs_allowed
print(f"20. Subsidy vs Allowed: {subsidy_vs_allowed:.2f}")

if not pd.isna(dealer_lat) and not pd.isna(dealer_lon):
    try:
        distance = haversine((feature_dict['geo_lat'], feature_dict['geo_lon']), (dealer_lat, dealer_lon))
        feature_dict['distance_farmer_to_dealer_km'] = distance
        print(f"21. Distance Farmer to Dealer: {distance:.2f} km")
    except:
        feature_dict['distance_farmer_to_dealer_km'] = 0
        print(f"21. Distance Farmer to Dealer: 0 km (error)")
else:
    feature_dict['distance_farmer_to_dealer_km'] = 0
    print(f"21. Distance Farmer to Dealer: 0 km (missing)")

try:
    txn_dt = pd.to_datetime(sample_input["txn_date"])
    feature_dict['txn_day'] = txn_dt.day
    feature_dict['txn_month'] = txn_dt.month
    print(f"22. Transaction Day: {feature_dict['txn_day']}")
    print(f"23. Transaction Month: {feature_dict['txn_month']}")
except:
    feature_dict['txn_day'] = 1
    feature_dict['txn_month'] = 1

try:
    txn_time = pd.to_datetime(sample_input["txn_time"], format='%H:%M:%S')
    feature_dict['txn_hour'] = txn_time.hour
    print(f"24. Transaction Hour: {feature_dict['txn_hour']}")
except:
    feature_dict['txn_hour'] = 12

# Remaining features (25-32)
feature_dict['txn_week'] = 1
feature_dict['txn_day_of_week'] = 0
feature_dict['farmer_avg_qty'] = farmer_qty_total / max(farmer_txn_count, 1)
feature_dict['dealer_avg_qty'] = dealer_qty_total / max(dealer_txn_count, 1)
feature_dict['subsidy_per_kg'] = subsidy_amount / max(quantity_kg, 0.1)
feature_dict['quantity_pct_of_allowed'] = (quantity_kg / max(allowed_quantity, 0.1)) * 100
feature_dict['subsidy_pct_of_allowed'] = (subsidy_amount / max(max_subsidy, 0.1)) * 100
feature_dict['land_eligibility_pct'] = ((land - eligibility_min) / max(eligibility_max - eligibility_min, 0.1)) * 100 if eligibility_max else 0

print("\n--- Building Feature Vector ---")

feature_order = ['quantity_kg', 'subsidy_amount', 'geo_lat', 'geo_lon', 'claimed_land_area_ha',
                 'amount_paid_by_farmer', 'land_holding_ha', 'lat', 'lon', 'num_outlets',
                 'avg_monthly_txn', 'inventory_received_kg', 'suspicious_dealer',
                 'max_qty_per_ha', 'max_subsidy_amount', 'eligibility_land_min', 'eligibility_land_max',
                 'quantity_per_hectare', 'land_vs_claim_diff', 'farmer_total_transactions', 'farmer_total_quantity',
                 'dealer_total_farmers', 'dealer_total_transactions', 'dealer_total_quantity',
                 'invoice_duplicate_flag', 'allowed_quantity', 'quantity_vs_allowed', 'subsidy_vs_allowed',
                 'distance_farmer_to_dealer_km', 'txn_hour', 'txn_day', 'txn_month']

feature_row = pd.DataFrame([feature_dict])
feature_row = feature_row[feature_order]
feature_row = feature_row.fillna(0)

print(f"Feature DataFrame shape: {feature_row.shape}")

feature_scaled = scaler.transform(feature_row)

print("\n--- Model Predictions ---")

iso_score = isolation_model.decision_function(feature_scaled)[0]
print(f"IsolationForest Decision Function Score: {iso_score:.4f}")

if use_xgb:
    xgb_proba = xgb_model.predict_proba(feature_scaled)[0][1]
    print(f"XGBoost Fraud Probability: {xgb_proba:.4f}")
    
    # Score weights: 70% XGBoost, 30% Isolation Forest
    iso_normalized = (iso_score + 1) / 2  # Convert from [-1,1] to [0,1]
    risk_score = (xgb_proba * 0.7) + (iso_normalized * 0.3)
    
    print(f"\nScore Calculation:")
    print(f"  XGBoost Fraud Probability: {xgb_proba:.4f} x 70% = {xgb_proba * 0.7:.4f}")
    print(f"  Isolation Forest (normalized): {iso_normalized:.4f} x 30% = {iso_normalized * 0.3:.4f}")
else:
    xgb_proba = None
    iso_normalized = (iso_score + 1) / 2
    risk_score = iso_normalized
    print(f"XGBoost not available, using Isolation Forest only")

print(f"\nFinal Risk Score: {risk_score:.4f}")

# Risk level classification
if risk_score >= 0.6:
    risk_level = "HIGH RISK"
elif risk_score >= 0.3:
    risk_level = "MEDIUM RISK"
else:
    risk_level = "LOW RISK"

print(f"Risk Level: {risk_level}")

print("\n--- Final Decision ---\n")

# SIMPLE RULE-BASED DECISION
risk_factors = []

# Flag 1: Ghost Farmer
if is_ghost_farmer:
    risk_factors.append({
        'severity': 'CRITICAL',
        'condition': 'Ghost Farmer',
        'detail': f'Farmer ID {sample_input["farmer_id"]} not found in master registry'
    })

# Flag 2: Quantity over limit
if quantity_vs_allowed > 0:
    risk_factors.append({
        'severity': 'HIGH',
        'condition': 'Quantity Exceeded',
        'detail': f'Claimed {quantity_kg:.2f} kg > Allowed {allowed_quantity:.2f} kg (excess: {quantity_vs_allowed:.2f} kg)'
    })

# Flag 3: Subsidy over limit
if subsidy_vs_allowed > 0:
    risk_factors.append({
        'severity': 'HIGH',
        'condition': 'Subsidy Exceeded',
        'detail': f'Claimed Rs {subsidy_amount:.2f} > Allowed Rs {max_subsidy:.2f} (excess: Rs {subsidy_vs_allowed:.2f})'
    })

# Flag 4: Land claim inflation (> 5x difference)
if land > 0 and land_vs_claim > land * 5:
    risk_factors.append({
        'severity': 'HIGH',
        'condition': 'Land Claim Inflated',
        'detail': f'Claimed {sample_input.get("claimed_land_area_ha", 0):.2f} ha vs Actual {land:.2f} ha (difference: {land_vs_claim:.2f} ha)'
    })
elif land > 0 and land_vs_claim > land * 2:
    risk_factors.append({
        'severity': 'MEDIUM',
        'condition': 'Land Claim Suspicious',
        'detail': f'Claimed {sample_input.get("claimed_land_area_ha", 0):.2f} ha vs Actual {land:.2f} ha (difference: {land_vs_claim:.2f} ha)'
    })

# Flag 5: Extreme distance (>500 km)
distance_km = feature_dict.get('distance_farmer_to_dealer_km', 0)
if distance_km > 1000:
    risk_factors.append({
        'severity': 'HIGH',
        'condition': 'Extreme Distance',
        'detail': f'Transaction location {distance_km:.0f} km away from farmer (potential dealer fraud)'
    })
elif distance_km > 500:
    risk_factors.append({
        'severity': 'MEDIUM',
        'condition': 'High Distance',
        'detail': f'Transaction location {distance_km:.0f} km away from farmer'
    })

# Flag 6: Suspicious payment/delivery mode (Cash + ManualEntry)
payment_mode = sample_input.get("payment_mode", "")
delivery_mode = sample_input.get("mode_of_delivery", "")
if payment_mode == "Cash" and delivery_mode == "ManualEntry":
    risk_factors.append({
        'severity': 'HIGH',
        'condition': 'Suspicious Payment Mode',
        'detail': f'Cash payment with Manual entry (no digital trail)'
    })

# Flag 7: Invoice duplicate
if feature_dict.get('invoice_duplicate_flag', 0) == 1:
    risk_factors.append({
        'severity': 'HIGH',
        'condition': 'Invoice Duplicate',
        'detail': f'Invoice {sample_input.get("invoice_no", "N/A")} already used by this dealer'
    })

# Flag 8: Season mismatch (REMOVED - Only crops have seasonal constraints, not products)
# Products like Urea, DAP, Seeds are available year-round in subsidies
# Only recommend seasonal products, don't penalize them

# Flag 8b: Crop season mismatch (if crop_type provided)
crop_type = sample_input.get("crop_type", None)
if crop_type:
    try:
        txn_date = pd.to_datetime(sample_input["txn_date"])
        month = txn_date.month
        
        seasons = {
            "Rabi (Oct-Mar)": {
                "months": [10, 11, 12, 1, 2, 3],
                "crops": ["Wheat", "Paddy", "Pulses"]
            },
            "Kharif (Jun-Sep)": {
                "months": [6, 7, 8, 9],
                "crops": ["Maize", "Cotton", "Sugarcane"]
            },
            "Summer (Apr-May)": {
                "months": [4, 5],
                "crops": ["Vegetables"]
            }
        }
        
        for season_name, season_data in seasons.items():
            if month in season_data["months"]:
                if crop_type not in season_data["crops"]:
                    risk_factors.append({
                        'severity': 'MEDIUM',
                        'condition': 'Wrong Crop Season',
                        'detail': f'{crop_type} not grown in {season_name} (expected: {", ".join(season_data["crops"])})'
                    })
                break
    except:
        pass

# Flag 9: Very high quantity per hectare
qty_per_ha = feature_dict.get('quantity_per_hectare', 0)
if qty_per_ha > 200:
    risk_factors.append({
        'severity': 'HIGH',
        'condition': 'Extreme Quantity/Ha',
        'detail': f'{qty_per_ha:.2f} kg/ha (normal: 30-60 kg/ha)'
    })
elif qty_per_ha > 100:
    risk_factors.append({
        'severity': 'MEDIUM',
        'condition': 'High Quantity/Ha',
        'detail': f'{qty_per_ha:.2f} kg/ha (normal: 30-60 kg/ha)'
    })

# Flag 10: Tiny quantity inconsistent with typical patterns
if quantity_kg > 0 and quantity_kg < 0.5:
    risk_factors.append({
        'severity': 'MEDIUM',
        'condition': 'Unusually Tiny Quantity',
        'detail': f'{quantity_kg:.2f} kg is anomalously small (typical: 10-100 kg)'
    })

# Display results
print("="*70)
if risk_factors:
    print("[RISK DETECTED] - FRAUD ALERT")
    print("="*70)
    print(f"\nTotal Risk Factors Found: {len(risk_factors)}\n")
    
    # Group by severity
    critical = [f for f in risk_factors if f['severity'] == 'CRITICAL']
    high = [f for f in risk_factors if f['severity'] == 'HIGH']
    medium = [f for f in risk_factors if f['severity'] == 'MEDIUM']
    
    if critical:
        print("CRITICAL ISSUES:")
        for i, f in enumerate(critical, 1):
            print(f"  {i}. {f['condition']}")
            print(f"     -> {f['detail']}\n")
    
    if high:
        print("HIGH RISK ISSUES:")
        for i, f in enumerate(high, 1):
            print(f"  {i}. {f['condition']}")
            print(f"     -> {f['detail']}\n")
    
    if medium:
        print("MEDIUM RISK ISSUES:")
        for i, f in enumerate(medium, 1):
            print(f"  {i}. {f['condition']}")
            print(f"     -> {f['detail']}\n")
    
    print(f"Overall Risk Level: {risk_level}")
    print(f"Risk Score: {risk_score:.4f}")
    print("="*70)
    print("RECOMMENDATION: REJECT TRANSACTION - FLAG FOR INVESTIGATION")
    print("="*70)
else:
    print("[TRANSACTION SAFE] - NO RED FLAGS")
    print("="*70)
    print("All checks passed:")
    print("  OK Farmer registered in system")
    print("  OK Quantity within limits")
    print("  OK Subsidy within limits")
    print("  OK Land claim reasonable")
    print("  OK Location plausible")
    print("  OK Payment mode standard")
    print(f"\nRisk Score: {risk_score:.4f} ({risk_level})")
    print("="*70)
    print("RECOMMENDATION: APPROVE TRANSACTION")

print("\nPrediction complete.")
