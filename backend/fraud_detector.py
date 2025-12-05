"""
Agricultural Subsidy Leakage Detection Model

This module implements anomaly detection algorithms to identify fraudulent patterns in 
agricultural subsidy applications, including:
- Ghost farmer detection (unrealistic land holdings)
- Excessive subsidy claims compared to land size
- Geographically clustered suspicious applications
- Dealer-level fraud patterns
- Statistical anomalies in fertilizer/seed requirements

Based on Isolation Forest and statistical methods for detecting outliers.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import joblib
import os


class SubsidyFraudDetector:
    """
    ML-based fraud detection for agricultural subsidy applications.
    
    Detects anomalies based on:
    1. Land size vs crop type expected norms
    2. Geographic clustering of applications
    3. Temporal patterns (sudden spikes)
    4. Deviation from standard fertilizer/seed requirements
    """
    
    def __init__(self, crop_norms_path='data/crop_norms.csv'):
        """Initialize the fraud detector with crop norms data."""
        self.crop_norms_path = crop_norms_path
        self.crop_norms = self._load_crop_norms()
        self.isolation_forest = None
        self.scaler = StandardScaler()
        self.trained = False
        
    def _load_crop_norms(self):
        """Load crop-specific fertilizer and seed norms."""
        try:
            norms = pd.read_csv(self.crop_norms_path)
            # Create normalized crop names for matching
            norms['crop_normalized'] = norms['crop'].str.lower().str.strip()
            return norms
        except FileNotFoundError:
            print(f"Warning: {self.crop_norms_path} not found. Using default norms.")
            return pd.DataFrame({
                'crop': ['Paddy', 'Wheat', 'Cotton', 'Sugarcane'],
                'fertilizer_kg_per_acre': [50, 45, 40, 60],
                'seed_kg_per_acre': [2, 2.5, 1, 3],
                'crop_normalized': ['paddy', 'wheat', 'cotton', 'sugarcane']
            })
    
    def get_crop_norm(self, crop_name):
        """Get expected fertilizer and seed requirements for a crop."""
        crop_normalized = crop_name.lower().strip()
        
        # Try exact match first
        match = self.crop_norms[self.crop_norms['crop_normalized'] == crop_normalized]
        
        if not match.empty:
            return {
                'fertilizer_per_acre': float(match.iloc[0]['fertilizer_kg_per_acre']),
                'seed_per_acre': float(match.iloc[0]['seed_kg_per_acre'])
            }
        
        # Try partial match
        for _, row in self.crop_norms.iterrows():
            if crop_normalized in row['crop_normalized'] or row['crop_normalized'] in crop_normalized:
                return {
                    'fertilizer_per_acre': float(row['fertilizer_kg_per_acre']),
                    'seed_per_acre': float(row['seed_kg_per_acre'])
                }
        
        # Return average if no match found
        return {
            'fertilizer_per_acre': self.crop_norms['fertilizer_kg_per_acre'].mean(),
            'seed_per_acre': self.crop_norms['seed_kg_per_acre'].mean()
        }
    

    def calculate_allowed_quantity(self, crop_type, land_size_acres, subsidy_type='fertilizer'):
        """
        Calculate allowed quantity based on government norms.
        
        Args:
            crop_type: Name of the crop
            land_size_acres: Farmer's land size in acres
            subsidy_type: 'fertilizer' or 'seed'
            
        Returns:
            dict with allowed quantity and rate per acre
        """
        norms = self.get_crop_norm(crop_type)
        
        if subsidy_type == 'fertilizer':
            rate_per_acre = norms['fertilizer_per_acre']
        elif subsidy_type == 'seed':
            rate_per_acre = norms['seed_per_acre']
        else:
            raise ValueError("subsidy_type must be 'fertilizer' or 'seed'")
        
        allowed_qty = land_size_acres * rate_per_acre
        
        return {
            'allowed_qty': round(allowed_qty, 2),
            'rate_per_acre': rate_per_acre,
            'land_size_acres': land_size_acres,
            'crop_type': crop_type,
            'subsidy_type': subsidy_type
        }
    
    def check_eligibility(self, crop_type, land_size_acres, requested_qty, subsidy_type='fertilizer'):
        """
        Check if requested quantity is within allowed limits (USE CASE 2: Fraud Prevention).
        
        Args:
            crop_type: Name of the crop
            land_size_acres: Farmer's land size in acres
            requested_qty: Requested subsidy quantity (kg)
            subsidy_type: 'fertilizer' or 'seed'
            
        Returns:
            dict with approval status, allowed quantity, and reason
        """
        allowed = self.calculate_allowed_quantity(crop_type, land_size_acres, subsidy_type)
        allowed_qty = allowed['allowed_qty']
        
        # Calculate qty_ratio for fraud detection
        qty_ratio = requested_qty / allowed_qty if allowed_qty > 0 else float('inf')
        
        # Determine approval status
        if requested_qty <= allowed_qty:
            approved = True
            reason = 'APPROVED'
            risk_flag = 'NORMAL'
        elif requested_qty <= allowed_qty * 1.1:  # 10% tolerance
            approved = True
            reason = 'APPROVED_WITH_TOLERANCE'
            risk_flag = 'LOW'
        else:
            approved = False
            reason = 'ABOVE_MAX_LIMIT'
            risk_flag = 'HIGH'
        
        # Additional fraud indicators
        fraud_indicators = []
        if qty_ratio > 1.5:
            fraud_indicators.append(f"Requested {qty_ratio:.1f}x the allowed limit - HIGH RISK")
        elif qty_ratio > 1.0:
            fraud_indicators.append(f"Requested {qty_ratio:.2f}x the allowed limit ({requested_qty:.0f}kg vs {allowed_qty:.0f}kg allowed)")
        if qty_ratio < 0.2 and requested_qty > 0:
            fraud_indicators.append("Suspiciously low request (possible ghost farmer pattern)")
        
        return {
            'approved': approved,
            'reason': reason,
            'risk_flag': risk_flag,
            'allowed_qty': allowed_qty,
            'requested_qty': requested_qty,
            'qty_ratio': round(qty_ratio, 3),
            'rate_per_acre': allowed['rate_per_acre'],
            'fraud_indicators': fraud_indicators if fraud_indicators else None
        }
    def extract_features(self, applications_df):
        """
        Extract features from applications for anomaly detection.
        
        Features:
        - Land size (acres)
        - Expected vs actual fertilizer requirement ratio
        - Geographic clustering score
        - Temporal clustering score
        - Land size deviation from district average
        """
        if applications_df.empty:
            return pd.DataFrame()
        
        features = []
        
        for idx, app in applications_df.iterrows():
            # Get crop norms
            norms = self.get_crop_norm(app['crop_type'])
            expected_fertilizer = norms['fertilizer_per_acre'] * app['total_land_acres']
            
            # Calculate feature values
            feature_dict = {
                'application_id': app['application_id'],
                'land_acres': app['total_land_acres'],
                'expected_fertilizer_total': expected_fertilizer,
                'land_size_category': self._categorize_land_size(app['total_land_acres']),
            }
            
            # Geographic clustering: count applications from same district
            district_count = len(applications_df[applications_df['district'] == app['district']])
            feature_dict['district_application_density'] = district_count
            
            # Calculate district average land size
            district_apps = applications_df[applications_df['district'] == app['district']]
            district_avg_land = district_apps['total_land_acres'].mean()
            feature_dict['land_deviation_from_district_avg'] = abs(app['total_land_acres'] - district_avg_land)
            
            # State-level statistics
            state_count = len(applications_df[applications_df['state'] == app['state']])
            feature_dict['state_application_count'] = state_count
            
            # Check for unrealistic land holdings (outlier detection)
            feature_dict['is_large_holding'] = 1 if app['total_land_acres'] > 100 else 0
            feature_dict['is_small_holding'] = 1 if app['total_land_acres'] < 0.5 else 0
            
            features.append(feature_dict)
        
        return pd.DataFrame(features)
    
    def _categorize_land_size(self, acres):
        """Categorize land size into bins."""
        if acres < 2:
            return 1  # Marginal farmer
        elif acres < 5:
            return 2  # Small farmer
        elif acres < 10:
            return 3  # Medium farmer
        else:
            return 4  # Large farmer
    
    def train(self, applications_df, contamination=0.1):
        """
        Train the Isolation Forest model on historical applications.
        
        Args:
            applications_df: DataFrame with application data
            contamination: Expected proportion of outliers (default 10%)
        """
        if applications_df.empty:
            print("No training data available.")
            return
        
        # Extract features
        features_df = self.extract_features(applications_df)
        
        if features_df.empty:
            print("No features extracted.")
            return
        
        # Select numerical features for training
        numerical_features = [
            'land_acres',
            'expected_fertilizer_total',
            'district_application_density',
            'land_deviation_from_district_avg',
            'state_application_count',
            'is_large_holding',
            'is_small_holding'
        ]
        
        X = features_df[numerical_features].fillna(0)
        
        # Standardize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.isolation_forest.fit(X_scaled)
        self.trained = True
        
        print(f"Model trained on {len(X)} applications.")
        print(f"Expected anomaly rate: {contamination * 100}%")
    
    def predict_anomalies(self, applications_df):
        """
        Detect anomalies in applications.
        
        Returns:
            DataFrame with application_id, anomaly_score, is_anomaly, risk_level, and reasons
        """
        if not self.trained:
            print("Model not trained. Training on provided data...")
            self.train(applications_df)
        
        if applications_df.empty:
            return pd.DataFrame()
        
        # Extract features
        features_df = self.extract_features(applications_df)
        
        numerical_features = [
            'land_acres',
            'expected_fertilizer_total',
            'district_application_density',
            'land_deviation_from_district_avg',
            'state_application_count',
            'is_large_holding',
            'is_small_holding'
        ]
        
        X = features_df[numerical_features].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Predict anomalies (-1 for anomalies, 1 for normal)
        predictions = self.isolation_forest.predict(X_scaled)
        scores = self.isolation_forest.score_samples(X_scaled)
        
        # Create results DataFrame
        results = pd.DataFrame({
            'application_id': features_df['application_id'],
            'anomaly_score': -scores,  # Invert so higher = more anomalous
            'is_anomaly': predictions == -1,
            'land_acres': features_df['land_acres'],
            'district_density': features_df['district_application_density'],
            'land_deviation': features_df['land_deviation_from_district_avg']
        })
        
        # Add risk level categorization
        results['risk_level'] = results['anomaly_score'].apply(self._calculate_risk_level)
        
        # Generate fraud reasons
        results['fraud_indicators'] = results.apply(
            lambda row: self._generate_fraud_reasons(row, applications_df), axis=1
        )
        
        return results.sort_values('anomaly_score', ascending=False)
    
    def _calculate_risk_level(self, anomaly_score):
        """Categorize risk based on anomaly score."""
        if anomaly_score > 0.6:
            return 'HIGH'
        elif anomaly_score > 0.4:
            return 'MEDIUM'
        elif anomaly_score > 0.2:
            return 'LOW'
        else:
            return 'NORMAL'
    
    def _generate_fraud_reasons(self, row, applications_df):
        """Generate human-readable fraud indicators."""
        reasons = []
        
        # Check land size anomalies
        if row['land_acres'] > 100:
            reasons.append(f"Unusually large land holding ({row['land_acres']:.1f} acres)")
        elif row['land_acres'] < 0.5:
            reasons.append(f"Extremely small land holding ({row['land_acres']:.1f} acres)")
        
        # Check geographic clustering
        if row['district_density'] > 50:
            reasons.append(f"High application density in district ({row['district_density']} applications)")
        
        # Check land deviation
        if row['land_deviation'] > 20:
            reasons.append(f"Land size significantly different from district average (±{row['land_deviation']:.1f} acres)")
        
        # General anomaly flag
        if row['is_anomaly']:
            reasons.append("Statistical anomaly detected by ML model")
        
        return reasons if reasons else ['No specific indicators']
    
    def get_fraud_statistics(self, applications_df):
        """
        Generate fraud statistics and insights.
        
        Returns:
            Dictionary with fraud statistics
        """
        results = self.predict_anomalies(applications_df)
        
        stats = {
            'total_applications': len(applications_df),
            'flagged_anomalies': int(results['is_anomaly'].sum()),
            'anomaly_percentage': float(results['is_anomaly'].mean() * 100),
            'high_risk_count': int((results['risk_level'] == 'HIGH').sum()),
            'medium_risk_count': int((results['risk_level'] == 'MEDIUM').sum()),
            'low_risk_count': int((results['risk_level'] == 'LOW').sum()),
            'top_risk_applications': results.nlargest(10, 'anomaly_score')[
                ['application_id', 'anomaly_score', 'risk_level', 'fraud_indicators']
            ].to_dict('records')
        }
        
        return stats
    
    def save_model(self, filepath='fraud_detection_model.pkl'):
        """Save trained model to disk."""
        if not self.trained:
            print("Model not trained yet.")
            return
        
        model_data = {
            'isolation_forest': self.isolation_forest,
            'scaler': self.scaler,
            'crop_norms': self.crop_norms
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='fraud_detection_model.pkl'):
        """Load trained model from disk."""
        if not os.path.exists(filepath):
            print(f"Model file {filepath} not found.")
            return
        
        model_data = joblib.load(filepath)
        self.isolation_forest = model_data['isolation_forest']
        self.scaler = model_data['scaler']
        self.crop_norms = model_data['crop_norms']
        self.trained = True
        print(f"Model loaded from {filepath}")


def main():
    """Example usage of the fraud detector."""
    # Sample applications data
    sample_data = pd.DataFrame({
        'application_id': ['APP001', 'APP002', 'APP003', 'APP004', 'APP005'],
        'farmer_name': ['Farmer A', 'Farmer B', 'Farmer C', 'Farmer D', 'Farmer E'],
        'total_land_acres': [5, 2, 150, 3, 4],  # APP003 has unusually large land
        'crop_type': ['Paddy', 'Wheat', 'Cotton', 'Paddy', 'Maize'],
        'district': ['District1', 'District1', 'District2', 'District1', 'District3'],
        'state': ['State1', 'State1', 'State2', 'State1', 'State3']
    })
    
    # Initialize detector
    detector = SubsidyFraudDetector()
    
    # Train model
    detector.train(sample_data, contamination=0.2)
    
    # Detect anomalies
    results = detector.predict_anomalies(sample_data)
    print("\nAnomaly Detection Results:")
    print(results)
    
    # Get fraud statistics
    stats = detector.get_fraud_statistics(sample_data)
    print("\nFraud Statistics:")
    for key, value in stats.items():
        if key != 'top_risk_applications':
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()




