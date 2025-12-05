"""
ML-Integrated Fraud Detection System
Combines Hackathon_Nitro ML models with application fraud detection
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Add Hackathon_Nitro to path
HACKATHON_DIR = Path(__file__).parent.parent / "Hackathon_Nitro"
sys.path.insert(0, str(HACKATHON_DIR))

class MLIntegratedFraudDetector:
    """Integrated ML fraud detection using Hackathon_Nitro models"""
    
    def __init__(self):
        self.models_dir = HACKATHON_DIR / "models"
        self.data_dir = HACKATHON_DIR
        self.models_loaded = False
        self.load_models()
        self.load_reference_data()
        
    def load_models(self):
        """Load pre-trained ML models"""
        try:
            self.isolation_forest = joblib.load(self.models_dir / "isolation_forest.pkl")
            self.scaler = joblib.load(self.models_dir / "feature_scaler.pkl")
            
            # Try to load XGBoost model
            try:
                self.xgboost_model = joblib.load(self.models_dir / "xgboost_model.pkl")
                self.use_xgb = True
            except:
                self.use_xgb = False
                print("Warning: XGBoost model not found, using Isolation Forest only")
            
            # Load metrics summary
            with open(self.models_dir / "metrics_summary.json", "r") as f:
                self.metrics = json.load(f)
            
            self.models_loaded = True
            print("✓ ML models loaded successfully")
            
        except Exception as e:
            print(f"Error loading ML models: {str(e)}")
            self.models_loaded = False
    
    def load_reference_data(self):
        """Load reference datasets"""
        try:
            self.farmers_df = pd.read_csv(self.data_dir / "farmers.csv")
            self.dealers_df = pd.read_csv(self.data_dir / "dealers.csv")
            self.scheme_rules_df = pd.read_csv(self.data_dir / "scheme_rules.csv")
            self.transactions_df = pd.read_csv(self.data_dir / "transactions.csv")
            
            print(f"✓ Loaded reference data: {len(self.farmers_df)} farmers, {len(self.dealers_df)} dealers, {len(self.transactions_df)} transactions")
            
        except Exception as e:
            print(f"Error loading reference data: {str(e)}")
    
    def engineer_features(self, application: Dict[str, Any]) -> Dict[str, Any]:
        """Engineer features from application data (32 features)"""
        
        features = {}
        
        # Basic quantity and subsidy features
        features['quantity_kg'] = application.get('fertilizer_qty', 0) + application.get('seed_qty', 0)
        features['subsidy_amount'] = features['quantity_kg'] * 10  # Estimated at 10 INR per kg
        
        # Geographic features (defaults for demo)
        features['geo_lat'] = 18.5204  # Default latitude (Pune)
        features['geo_lon'] = 73.8567  # Default longitude (Pune)
        
        # Land features
        features['claimed_land_area_ha'] = application.get('total_land_acres', 0) * 0.404686  # Convert to hectares
        features['amount_paid_by_farmer'] = features['subsidy_amount'] * 0.3  # Assume 30% farmer contribution
        features['land_holding_ha'] = features['claimed_land_area_ha']  # Same for new applications
        
        # Dealer location features (defaults)
        features['lat'] = 18.5204
        features['lon'] = 73.8567
        features['num_outlets'] = 1
        features['avg_monthly_txn'] = 50
        features['inventory_received_kg'] = 10000
        features['suspicious_dealer'] = 0
        
        # Scheme rule features
        features['max_qty_per_ha'] = 100  # kg per hectare limit
        features['max_subsidy_amount'] = features['claimed_land_area_ha'] * 100 * 10  # Based on land
        features['eligibility_land_min'] = 0.1  # Minimum 0.1 hectares
        features['eligibility_land_max'] = 50.0  # Maximum 50 hectares
        
        # Derived features
        features['quantity_per_hectare'] = features['quantity_kg'] / max(features['claimed_land_area_ha'], 0.1)
        features['land_vs_claim_diff'] = 0  # No difference for new farmers
        
        # Farmer transaction history (defaults for new farmers)
        features['farmer_total_transactions'] = 1
        features['farmer_total_quantity'] = features['quantity_kg']
        
        # Dealer transaction history (defaults)
        features['dealer_total_farmers'] = 50
        features['dealer_total_transactions'] = 100
        features['dealer_total_quantity'] = 5000
        
        # Invoice and quantity validation
        features['invoice_duplicate_flag'] = 0
        features['allowed_quantity'] = features['claimed_land_area_ha'] * features['max_qty_per_ha']
        features['quantity_vs_allowed'] = features['quantity_kg'] / max(features['allowed_quantity'], 1)
        features['subsidy_vs_allowed'] = features['subsidy_amount'] / max(features['max_subsidy_amount'], 1)
        
        # Distance features
        features['distance_farmer_to_dealer_km'] = 5.0  # Default reasonable distance
        
        # Time features
        now = datetime.now()
        features['txn_hour'] = now.hour
        features['txn_day'] = now.day
        features['txn_month'] = now.month
        
        return features
    
    def prepare_features_for_model(self, features: Dict[str, Any]) -> np.ndarray:
        """Prepare features in the correct order for model prediction (32 features)"""
        
        # Expected feature names from training (exact order matters)
        feature_names = [
            'quantity_kg', 'subsidy_amount', 'geo_lat', 'geo_lon',
            'claimed_land_area_ha', 'amount_paid_by_farmer', 'land_holding_ha',
            'lat', 'lon', 'num_outlets', 'avg_monthly_txn', 'inventory_received_kg',
            'suspicious_dealer', 'max_qty_per_ha', 'max_subsidy_amount',
            'eligibility_land_min', 'eligibility_land_max', 'quantity_per_hectare',
            'land_vs_claim_diff', 'farmer_total_transactions', 'farmer_total_quantity',
            'dealer_total_farmers', 'dealer_total_transactions', 'dealer_total_quantity',
            'invoice_duplicate_flag', 'allowed_quantity', 'quantity_vs_allowed',
            'subsidy_vs_allowed', 'distance_farmer_to_dealer_km', 'txn_hour',
            'txn_day', 'txn_month'
        ]
        
        # Create feature vector
        feature_vector = []
        for name in feature_names:
            feature_vector.append(features.get(name, 0))
        
        return np.array(feature_vector).reshape(1, -1)
    
    def predict_fraud(self, application: Dict[str, Any]) -> Dict[str, Any]:
        """Predict fraud probability for an application"""
        
        if not self.models_loaded:
            return {
                "fraud_score": 0.0,
                "is_fraud": False,
                "confidence": 0.0,
                "risk_level": "UNKNOWN",
                "warnings": ["ML models not loaded"],
                "details": {}
            }
        
        try:
            # Engineer features
            features = self.engineer_features(application)
            
            # Prepare feature vector
            X = self.prepare_features_for_model(features)
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Isolation Forest prediction (-1 for anomaly, 1 for normal)
            iso_pred = self.isolation_forest.predict(X_scaled)[0]
            iso_score = self.isolation_forest.decision_function(X_scaled)[0]
            
            # Convert to probability (higher score = more anomalous)
            iso_fraud_prob = 1 / (1 + np.exp(iso_score * 2))  # Sigmoid transformation
            
            # XGBoost prediction if available
            if self.use_xgb:
                xgb_fraud_prob = self.xgboost_model.predict_proba(X_scaled)[0][1]
                # Weighted average
                fraud_score = 0.6 * xgb_fraud_prob + 0.4 * iso_fraud_prob
                confidence = max(xgb_fraud_prob, iso_fraud_prob)
            else:
                fraud_score = iso_fraud_prob
                confidence = abs(iso_score)
            
            # Risk level determination - Binary: SAFE or RISK
            # Consider fraud if score > 0.5 OR if there are validation warnings
            has_warnings = False
            warnings = []
            
            # Check for validation warnings first
            quantity_per_hectare = features['quantity_per_hectare']
            if quantity_per_hectare > 200:
                warnings.append("Unusually high quantity per hectare")
                has_warnings = True
            if features['quantity_vs_allowed'] > 1.0:
                warnings.append("Requested quantity exceeds scheme limits")
                has_warnings = True
            if features['txn_hour'] > 22 or features['txn_hour'] < 6:
                warnings.append("Transaction at unusual hours")
                has_warnings = True
            if features['distance_farmer_to_dealer_km'] > 50:
                warnings.append("Large distance between farmer and dealer")
                has_warnings = True
            
            # Binary risk determination
            if fraud_score > 0.5 or has_warnings:
                risk_level = "RISK"
                is_fraud = True
            else:
                risk_level = "SAFE"
                is_fraud = False
            
            return {
                "fraud_score": round(float(fraud_score), 4),
                "is_fraud": bool(is_fraud),
                "confidence": round(float(confidence), 4),
                "risk_level": risk_level,
                "warnings": warnings,
                "details": {
                    "isolation_forest_score": round(float(iso_fraud_prob), 4),
                    "xgboost_score": round(float(xgb_fraud_prob), 4) if self.use_xgb else None,
                    "quantity_per_hectare": round(features['quantity_per_hectare'], 2),
                    "quantity_vs_allowed": round(features['quantity_vs_allowed'], 2),
                    "subsidy_amount": round(features['subsidy_amount'], 2),
                    "claimed_land_ha": round(features['claimed_land_area_ha'], 2),
                    "total_quantity_kg": round(features['quantity_kg'], 2),
                    "engineered_features": features
                }
            }
            
        except Exception as e:
            print(f"Error in fraud prediction: {str(e)}")
            return {
                "fraud_score": 0.0,
                "is_fraud": False,
                "confidence": 0.0,
                "risk_level": "ERROR",
                "warnings": [f"Prediction error: {str(e)}"],
                "details": {}
            }
    
    def get_farmer_insights(self, farmer_id: Optional[str] = None) -> Dict[str, Any]:
        """Get insights about farmers from historical data"""
        
        try:
            total_farmers = len(self.farmers_df)
            ghost_farmers = self.farmers_df['is_ghost_farmer'].sum() if 'is_ghost_farmer' in self.farmers_df.columns else 0
            
            # Transaction statistics
            avg_transactions = len(self.transactions_df) / total_farmers if total_farmers > 0 else 0
            
            # Fraud statistics
            fraud_count = self.transactions_df['is_suspected_fraud'].sum() if 'is_suspected_fraud' in self.transactions_df.columns else 0
            fraud_rate = fraud_count / len(self.transactions_df) if len(self.transactions_df) > 0 else 0
            
            return {
                "total_farmers": int(total_farmers),
                "ghost_farmers": int(ghost_farmers),
                "total_transactions": int(len(self.transactions_df)),
                "avg_transactions_per_farmer": round(avg_transactions, 2),
                "suspected_fraud_cases": int(fraud_count),
                "fraud_rate": round(fraud_rate * 100, 2),
                "model_metrics": self.metrics if hasattr(self, 'metrics') else {}
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_seasonal_recommendations(self) -> Dict[str, Any]:
        """Get seasonal product recommendations"""
        
        current_month = datetime.now().month
        
        seasons = {
            "Rabi": {
                "months": [10, 11, 12, 1, 2, 3],
                "products": ["Urea", "DAP", "Seeds", "Pesticide"],
                "crops": ["Wheat", "Barley", "Mustard", "Gram"]
            },
            "Kharif": {
                "months": [6, 7, 8, 9],
                "products": ["Urea", "DAP", "Seeds", "Pesticide"],
                "crops": ["Rice", "Maize", "Cotton", "Soybean"]
            },
            "Zaid": {
                "months": [4, 5],
                "products": ["Urea", "Seeds", "Pesticide"],
                "crops": ["Watermelon", "Cucumber", "Bitter Gourd"]
            }
        }
        
        current_season = None
        for season, info in seasons.items():
            if current_month in info["months"]:
                current_season = season
                break
        
        return {
            "current_month": current_month,
            "current_season": current_season,
            "recommended_products": seasons[current_season]["products"] if current_season else [],
            "recommended_crops": seasons[current_season]["crops"] if current_season else [],
            "all_seasons": seasons
        }
    
    def analyze_batch(self, applications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple applications in batch"""
        
        results = []
        for app in applications:
            prediction = self.predict_fraud(app)
            results.append({
                "application_id": app.get("application_id", "N/A"),
                "farmer_name": app.get("farmer_name", "N/A"),
                **prediction
            })
        
        return results

# Singleton instance
_ml_detector = None

def get_ml_integrated_detector():
    """Get singleton ML detector instance"""
    global _ml_detector
    if _ml_detector is None:
        _ml_detector = MLIntegratedFraudDetector()
    return _ml_detector
