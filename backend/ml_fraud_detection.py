"""
ML-Based Fraud Detection Integration
Integrates Hackathon_Nitro trained models with the farmer portal backend
"""

import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import json

class MLFraudDetector:
    """
    Advanced ML-based fraud detection using trained Isolation Forest and XGBoost models
    from Hackathon_Nitro datasets
    """
    
    def __init__(self, models_dir='../Hackathon_Nitro/models', data_dir='../Hackathon_Nitro'):
        """Initialize ML fraud detector with pre-trained models"""
        self.models_dir = Path(models_dir)
        self.data_dir = Path(data_dir)
        
        # Load trained models
        self.isolation_forest = None
        self.xgb_model = None
        self.scaler = None
        self.metrics = None
        
        # Load reference datasets
        self.farmers_df = None
        self.dealers_df = None
        self.transactions_df = None
        self.scheme_rules_df = None
        
        self._load_models()
        self._load_reference_data()
        
    def _load_models(self):
        """Load pre-trained ML models"""
        try:
            isolation_path = self.models_dir / 'isolation_forest.pkl'
            xgb_path = self.models_dir / 'xgboost_model.pkl'
            scaler_path = self.models_dir / 'feature_scaler.pkl'
            metrics_path = self.models_dir / 'metrics_summary.json'
            
            if isolation_path.exists():
                self.isolation_forest = joblib.load(isolation_path)
                print("✓ Loaded Isolation Forest model")
            
            if xgb_path.exists():
                self.xgb_model = joblib.load(xgb_path)
                print("✓ Loaded XGBoost model")
            
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
                print("✓ Loaded Feature Scaler")
            
            if metrics_path.exists():
                with open(metrics_path, 'r') as f:
                    self.metrics = json.load(f)
                print("✓ Loaded Model Metrics")
                
        except Exception as e:
            print(f"Warning: Error loading models - {str(e)}")
    
    def _load_reference_data(self):
        """Load reference datasets for feature engineering"""
        try:
            farmers_path = self.data_dir / 'farmers.csv'
            dealers_path = self.data_dir / 'dealers.csv'
            transactions_path = self.data_dir / 'transactions.csv'
            scheme_path = self.data_dir / 'scheme_rules.csv'
            
            if farmers_path.exists():
                self.farmers_df = pd.read_csv(farmers_path)
                print(f"✓ Loaded {len(self.farmers_df)} farmers records")
            
            if dealers_path.exists():
                self.dealers_df = pd.read_csv(dealers_path)
                print(f"✓ Loaded {len(self.dealers_df)} dealers records")
            
            if transactions_path.exists():
                self.transactions_df = pd.read_csv(transactions_path)
                print(f"✓ Loaded {len(self.transactions_df)} transactions records")
            
            if scheme_path.exists():
                self.scheme_rules_df = pd.read_csv(scheme_path)
                print(f"✓ Loaded {len(self.scheme_rules_df)} scheme rules")
                
        except Exception as e:
            print(f"Warning: Error loading reference data - {str(e)}")
    
    def engineer_features(self, transaction_data: Dict) -> pd.DataFrame:
        """
        Engineer features for a single transaction similar to feature_engineering.py
        """
        try:
            # Create base dataframe
            df = pd.DataFrame([transaction_data])
            
            # Basic features
            df['quantity_per_hectare'] = df.get('quantity_kg', 0) / max(df.get('claimed_land_area_ha', 0.1), 0.1)
            df['land_vs_claim_diff'] = df.get('claimed_land_area_ha', 0) - df.get('land_holding_ha', 0)
            
            # Farmer history features
            if self.transactions_df is not None and 'farmer_id' in transaction_data:
                farmer_id = transaction_data['farmer_id']
                farmer_txns = self.transactions_df[self.transactions_df['farmer_id'] == farmer_id]
                
                df['farmer_total_transactions'] = len(farmer_txns)
                df['farmer_total_quantity'] = farmer_txns['quantity_kg'].sum() if len(farmer_txns) > 0 else 0
            else:
                df['farmer_total_transactions'] = 0
                df['farmer_total_quantity'] = 0
            
            # Dealer features
            if self.transactions_df is not None and 'dealer_id' in transaction_data:
                dealer_id = transaction_data['dealer_id']
                dealer_txns = self.transactions_df[self.transactions_df['dealer_id'] == dealer_id]
                
                df['dealer_total_farmers'] = dealer_txns['farmer_id'].nunique()
                df['dealer_total_transactions'] = len(dealer_txns)
                df['dealer_total_quantity'] = dealer_txns['quantity_kg'].sum() if len(dealer_txns) > 0 else 0
            else:
                df['dealer_total_farmers'] = 0
                df['dealer_total_transactions'] = 0
                df['dealer_total_quantity'] = 0
            
            # Scheme rule features
            if self.scheme_rules_df is not None:
                product_type = transaction_data.get('product_type', 'Fertilizer')
                season = transaction_data.get('season', 'Rabi')
                
                rule = self.scheme_rules_df[
                    (self.scheme_rules_df['product_type'] == product_type) & 
                    (self.scheme_rules_df['season'] == season)
                ]
                
                if not rule.empty:
                    df['max_qty_per_ha'] = rule.iloc[0]['max_qty_per_ha']
                    df['max_subsidy_amount'] = rule.iloc[0]['max_subsidy_amount']
                else:
                    df['max_qty_per_ha'] = 100
                    df['max_subsidy_amount'] = 5000
                
                df['allowed_quantity'] = df['max_qty_per_ha'] * df.get('land_holding_ha', 1)
                df['quantity_vs_allowed'] = df.get('quantity_kg', 0) - df['allowed_quantity']
                df['subsidy_vs_allowed'] = df.get('subsidy_amount', 0) - df['max_subsidy_amount']
            
            # Time features
            if 'txn_date' in transaction_data:
                txn_date = pd.to_datetime(transaction_data['txn_date'])
                df['txn_month'] = txn_date.month
                df['txn_day'] = txn_date.day
            
            if 'txn_time' in transaction_data:
                txn_time = pd.to_datetime(transaction_data['txn_time'], format='%H:%M:%S', errors='coerce')
                df['txn_hour'] = txn_time.hour if pd.notna(txn_time) else 12
            
            return df
            
        except Exception as e:
            print(f"Error in feature engineering: {str(e)}")
            return pd.DataFrame()
    
    def predict_fraud(self, transaction_data: Dict) -> Dict:
        """
        Predict fraud probability for a transaction using both models
        
        Returns:
            Dict containing:
            - isolation_score: Anomaly score from Isolation Forest
            - xgb_probability: Fraud probability from XGBoost
            - risk_level: 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
            - reasons: List of suspicious indicators
            - recommendation: Action recommendation
        """
        result = {
            'isolation_score': 0.0,
            'xgb_probability': 0.0,
            'risk_level': 'LOW',
            'reasons': [],
            'recommendation': 'APPROVE',
            'details': {}
        }
        
        try:
            # Engineer features
            features_df = self.engineer_features(transaction_data)
            
            if features_df.empty:
                result['reasons'].append("Unable to engineer features")
                return result
            
            # Extract numeric features for prediction
            numeric_cols = features_df.select_dtypes(include=[np.number]).columns.tolist()
            X = features_df[numeric_cols].fillna(0)
            
            # Scale features
            if self.scaler is not None:
                try:
                    X_scaled = self.scaler.transform(X)
                except:
                    # If scaler fails, use unscaled features
                    X_scaled = X.values
            else:
                X_scaled = X.values
            
            # Isolation Forest prediction
            if self.isolation_forest is not None:
                iso_score = self.isolation_forest.decision_function(X_scaled)[0]
                iso_pred = self.isolation_forest.predict(X_scaled)[0]
                result['isolation_score'] = float(iso_score)
                result['details']['isolation_anomaly'] = bool(iso_pred == -1)
            
            # XGBoost prediction
            if self.xgb_model is not None:
                xgb_proba = self.xgb_model.predict_proba(X_scaled)[0][1]
                result['xgb_probability'] = float(xgb_proba)
            
            # Determine risk level based on both models
            risk_score = 0
            
            if result['isolation_score'] < -0.1:
                risk_score += 2
                result['reasons'].append("Isolation Forest detected anomaly")
            
            if result['xgb_probability'] > 0.7:
                risk_score += 3
                result['reasons'].append("High fraud probability from XGBoost")
            elif result['xgb_probability'] > 0.5:
                risk_score += 2
                result['reasons'].append("Moderate fraud probability")
            
            # Check business rules
            if 'quantity_vs_allowed' in features_df.columns:
                if features_df['quantity_vs_allowed'].iloc[0] > 0:
                    risk_score += 2
                    result['reasons'].append("Quantity exceeds allowed limit")
            
            if 'land_vs_claim_diff' in features_df.columns:
                if features_df['land_vs_claim_diff'].iloc[0] > 2:
                    risk_score += 1
                    result['reasons'].append("Land claim differs significantly from holdings")
            
            # Set risk level
            if risk_score >= 5:
                result['risk_level'] = 'CRITICAL'
                result['recommendation'] = 'REJECT'
            elif risk_score >= 3:
                result['risk_level'] = 'HIGH'
                result['recommendation'] = 'MANUAL_REVIEW'
            elif risk_score >= 1:
                result['risk_level'] = 'MEDIUM'
                result['recommendation'] = 'VERIFY_DOCUMENTS'
            else:
                result['risk_level'] = 'LOW'
                result['recommendation'] = 'APPROVE'
            
            # Add feature details
            result['details']['features'] = {
                'quantity_per_hectare': float(features_df['quantity_per_hectare'].iloc[0]) if 'quantity_per_hectare' in features_df.columns else 0,
                'farmer_total_transactions': int(features_df['farmer_total_transactions'].iloc[0]) if 'farmer_total_transactions' in features_df.columns else 0,
                'dealer_total_farmers': int(features_df['dealer_total_farmers'].iloc[0]) if 'dealer_total_farmers' in features_df.columns else 0
            }
            
        except Exception as e:
            result['reasons'].append(f"Prediction error: {str(e)}")
            result['risk_level'] = 'UNKNOWN'
            result['recommendation'] = 'MANUAL_REVIEW'
        
        return result
    
    def batch_predict(self, transactions: List[Dict]) -> List[Dict]:
        """Predict fraud for multiple transactions"""
        results = []
        for txn in transactions:
            result = self.predict_fraud(txn)
            result['transaction_id'] = txn.get('txn_id', 'unknown')
            results.append(result)
        return results
    
    def get_fraud_statistics(self) -> Dict:
        """Get fraud detection statistics from historical data"""
        stats = {
            'total_transactions': 0,
            'suspected_frauds': 0,
            'fraud_rate': 0.0,
            'model_metrics': self.metrics,
            'top_fraud_reasons': []
        }
        
        try:
            if self.transactions_df is not None:
                stats['total_transactions'] = len(self.transactions_df)
                
                if 'is_suspected_fraud' in self.transactions_df.columns:
                    suspected = self.transactions_df['is_suspected_fraud'].sum()
                    stats['suspected_frauds'] = int(suspected)
                    stats['fraud_rate'] = float(suspected / len(self.transactions_df) * 100)
                
                if 'fraud_reason' in self.transactions_df.columns:
                    reasons = self.transactions_df[self.transactions_df['is_suspected_fraud'] == True]['fraud_reason'].value_counts()
                    stats['top_fraud_reasons'] = [
                        {'reason': reason, 'count': int(count)} 
                        for reason, count in reasons.head(5).items()
                    ]
        except Exception as e:
            print(f"Error calculating statistics: {str(e)}")
        
        return stats
    
    def get_seasonal_recommendations(self, month: int) -> Dict:
        """Get seasonal product recommendations based on month"""
        seasons = {
            "Rabi": {
                "months": [10, 11, 12, 1, 2, 3],
                "products": ["Urea", "DAP", "Seeds", "Pesticide"],
                "crops": ["Wheat", "Mustard", "Barley", "Chickpea"]
            },
            "Kharif": {
                "months": [6, 7, 8, 9],
                "products": ["Urea", "DAP", "NPK", "Seeds"],
                "crops": ["Paddy", "Maize", "Cotton", "Soybean"]
            },
            "Zaid": {
                "months": [4, 5],
                "products": ["Fertilizer", "Seeds", "Pesticide"],
                "crops": ["Watermelon", "Cucumber", "Muskmelon"]
            }
        }
        
        for season, data in seasons.items():
            if month in data['months']:
                return {
                    'season': season,
                    'recommended_products': data['products'],
                    'recommended_crops': data['crops']
                }
        
        return {
            'season': 'Off-Season',
            'recommended_products': [],
            'recommended_crops': []
        }


# Global instance
ml_detector = None

def get_ml_detector() -> MLFraudDetector:
    """Get or create ML fraud detector instance"""
    global ml_detector
    if ml_detector is None:
        ml_detector = MLFraudDetector()
    return ml_detector
