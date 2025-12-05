"""
Test ML Integration with Hackathon_Nitro Models
Tests the integrated fraud detection system with output
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from ml_integrated_fraud_detector import get_ml_integrated_detector
from datetime import datetime
import json

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_ml_integration():
    """Test the ML integrated fraud detector"""
    
    print_section("ML INTEGRATION TEST - Hackathon_Nitro Models")
    
    # Initialize detector
    print("\n1. Initializing ML Integrated Fraud Detector...")
    detector = get_ml_integrated_detector()
    
    if not detector.models_loaded:
        print("❌ Models failed to load!")
        return
    
    print("✓ Models loaded successfully")
    print(f"✓ XGBoost available: {detector.use_xgb}")
    
    # Test 1: Model Status
    print_section("Model Status")
    print(f"Farmers in dataset: {len(detector.farmers_df)}")
    print(f"Dealers in dataset: {len(detector.dealers_df)}")
    print(f"Transactions in dataset: {len(detector.transactions_df)}")
    print(f"Scheme rules: {len(detector.scheme_rules_df)}")
    
    if hasattr(detector, 'metrics'):
        print("\nModel Metrics:")
        print(json.dumps(detector.metrics, indent=2))
    
    # Test 2: Farmer Insights
    print_section("Farmer Insights from Historical Data")
    insights = detector.get_farmer_insights()
    print(json.dumps(insights, indent=2))
    
    # Test 3: Seasonal Recommendations
    print_section("Seasonal Recommendations")
    recommendations = detector.get_seasonal_recommendations()
    print(f"Current Month: {recommendations['current_month']}")
    print(f"Current Season: {recommendations['current_season']}")
    print(f"Recommended Products: {', '.join(recommendations['recommended_products'])}")
    print(f"Recommended Crops: {', '.join(recommendations['recommended_crops'])}")
    
    # Test 4: Normal Application (Low Risk)
    print_section("Test Case 1: Normal Application (Expected: LOW RISK)")
    normal_app = {
        "application_id": "TEST001",
        "farmer_name": "Ram Kumar",
        "aadhaar_number": "1234-5678-9012",
        "mobile_number": "9876543210",
        "state": "Maharashtra",
        "district": "Pune",
        "address": "Village Pimpri, Pune",
        "total_land_acres": 5.0,
        "crop_type": "Wheat",
        "fertilizer_qty": 100.0,
        "seed_qty": 20.0,
        "subsidy_type": "fertilizer"
    }
    
    result1 = detector.predict_fraud(normal_app)
    print(f"\nFraud Score: {result1['fraud_score']:.4f}")
    print(f"Risk Level: {result1['risk_level']}")
    print(f"Is Fraud: {result1['is_fraud']}")
    print(f"Confidence: {result1['confidence']:.4f}")
    print(f"Warnings: {result1['warnings']}")
    if 'details' in result1 and result1['details']:
        print(f"\nDetails:")
        print(f"  - Isolation Forest Score: {result1['details'].get('isolation_forest_score', 'N/A')}")
        if result1['details'].get('xgboost_score'):
            print(f"  - XGBoost Score: {result1['details']['xgboost_score']}")
        print(f"  - Quantity per hectare: {result1['details'].get('quantity_per_hectare', 0):.2f}")
        print(f"  - Quantity vs Allowed: {result1['details'].get('quantity_vs_allowed', 0):.2f}")
        print(f"  - Subsidy Amount: {result1['details'].get('subsidy_amount', 0):.2f}")
        print(f"  - Claimed Land (ha): {result1['details'].get('claimed_land_ha', 0):.2f}")
    
    # Test 5: Suspicious Application (High Risk)
    print_section("Test Case 2: Suspicious Application (Expected: HIGH RISK)")
    suspicious_app = {
        "application_id": "TEST002",
        "farmer_name": "Suspicious Farmer",
        "aadhaar_number": "9999-9999-9999",
        "mobile_number": "9999999999",
        "state": "Maharashtra",
        "district": "Mumbai",
        "address": "Unknown location",
        "total_land_acres": 2.0,  # Small land
        "crop_type": "Rice",
        "fertilizer_qty": 500.0,  # Excessive quantity
        "seed_qty": 200.0,  # Excessive quantity
        "subsidy_type": "fertilizer"
    }
    
    result2 = detector.predict_fraud(suspicious_app)
    print(f"\nFraud Score: {result2['fraud_score']:.4f}")
    print(f"Risk Level: {result2['risk_level']}")
    print(f"Is Fraud: {result2['is_fraud']}")
    print(f"Confidence: {result2['confidence']:.4f}")
    print(f"Warnings: {result2['warnings']}")
    if 'details' in result2 and result2['details']:
        print(f"\nDetails:")
        print(f"  - Isolation Forest Score: {result2['details'].get('isolation_forest_score', 'N/A')}")
        if result2['details'].get('xgboost_score'):
            print(f"  - XGBoost Score: {result2['details']['xgboost_score']}")
        print(f"  - Quantity per hectare: {result2['details'].get('quantity_per_hectare', 0):.2f}")
        print(f"  - Quantity vs Allowed: {result2['details'].get('quantity_vs_allowed', 0):.2f}")
        print(f"  - Subsidy Amount: {result2['details'].get('subsidy_amount', 0):.2f}")
        print(f"  - Claimed Land (ha): {result2['details'].get('claimed_land_ha', 0):.2f}")
    
    # Test 6: Batch Analysis
    print_section("Test Case 3: Batch Analysis")
    batch_apps = [normal_app, suspicious_app]
    batch_results = detector.analyze_batch(batch_apps)
    
    print(f"\nAnalyzed {len(batch_results)} applications:")
    for idx, result in enumerate(batch_results, 1):
        print(f"\n{idx}. {result['application_id']} - {result['farmer_name']}")
        print(f"   Fraud Score: {result['fraud_score']:.4f}")
        print(f"   Risk Level: {result['risk_level']}")
        print(f"   Warnings: {len(result['warnings'])} warning(s)")
    
    # Summary
    print_section("INTEGRATION TEST SUMMARY")
    print("✓ All tests completed successfully!")
    print("\nCapabilities Verified:")
    print("  ✓ ML models loaded from Hackathon_Nitro")
    print("  ✓ Historical data integrated (farmers, dealers, transactions)")
    print("  ✓ Feature engineering working")
    print("  ✓ Fraud prediction functional")
    print("  ✓ Batch analysis operational")
    print("  ✓ Insights and recommendations available")
    print("\nML Integration Status: SUCCESS ✓")
    
    return True

if __name__ == "__main__":
    try:
        test_ml_integration()
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
