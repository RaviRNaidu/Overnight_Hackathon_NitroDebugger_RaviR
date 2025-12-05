"""
Test ML Integration - Verify ML models work with the backend
"""

import sys
sys.path.append('.')

from ml_fraud_detection import MLFraudDetector
from ml_data_processor import MLDataProcessor
import json

print("="*60)
print("ML INTEGRATION TEST")
print("="*60)

# Test 1: Initialize ML Detector
print("\n[Test 1] Initializing ML Fraud Detector...")
try:
    detector = MLFraudDetector(
        models_dir='../Hackathon_Nitro/models',
        data_dir='../Hackathon_Nitro'
    )
    print("✓ ML Fraud Detector initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize: {str(e)}")

# Test 2: Get Statistics
print("\n[Test 2] Getting Fraud Statistics...")
try:
    stats = detector.get_fraud_statistics()
    print(f"✓ Total Transactions: {stats['total_transactions']}")
    print(f"✓ Suspected Frauds: {stats['suspected_frauds']}")
    print(f"✓ Fraud Rate: {stats['fraud_rate']:.2f}%")
except Exception as e:
    print(f"✗ Failed to get statistics: {str(e)}")

# Test 3: Seasonal Recommendations
print("\n[Test 3] Getting Seasonal Recommendations...")
try:
    import datetime
    current_month = datetime.datetime.now().month
    recommendations = detector.get_seasonal_recommendations(current_month)
    print(f"✓ Current Season: {recommendations['season']}")
    print(f"✓ Recommended Products: {', '.join(recommendations['recommended_products'])}")
    print(f"✓ Recommended Crops: {', '.join(recommendations['recommended_crops'])}")
except Exception as e:
    print(f"✗ Failed to get recommendations: {str(e)}")

# Test 4: Fraud Prediction
print("\n[Test 4] Testing Fraud Prediction...")
try:
    sample_transaction = {
        'farmer_id': 'F001',
        'dealer_id': 'D001',
        'product_type': 'Fertilizer',
        'season': 'Rabi',
        'quantity_kg': 250,
        'claimed_land_area_ha': 3.0,
        'land_holding_ha': 2.0,
        'subsidy_amount': 5000,
        'txn_date': '2024-01-15',
        'txn_time': '10:30:00'
    }
    
    result = detector.predict_fraud(sample_transaction)
    print(f"✓ Risk Level: {result['risk_level']}")
    print(f"✓ Recommendation: {result['recommendation']}")
    print(f"✓ Isolation Score: {result['isolation_score']:.4f}")
    print(f"✓ XGBoost Probability: {result['xgb_probability']:.4f}")
    
    if result['reasons']:
        print(f"✓ Alert Reasons:")
        for reason in result['reasons']:
            print(f"  - {reason}")
    
except Exception as e:
    print(f"✗ Failed to predict fraud: {str(e)}")

# Test 5: Data Processor
print("\n[Test 5] Testing ML Data Processor...")
try:
    processor = MLDataProcessor(data_dir='../Hackathon_Nitro')
    processor.load_all_datasets()
    
    fraud_summary = processor.get_fraud_summary()
    print(f"✓ Total Transactions: {fraud_summary.get('total_transactions', 'N/A')}")
    print(f"✓ Total Frauds: {fraud_summary.get('total_frauds', 'N/A')}")
    
    farmer_analysis = processor.get_farmer_analysis()
    print(f"✓ Total Farmers: {farmer_analysis.get('total_farmers', 'N/A')}")
    
    dealer_analysis = processor.get_dealer_analysis()
    print(f"✓ Total Dealers: {dealer_analysis.get('total_dealers', 'N/A')}")
    
except Exception as e:
    print(f"✗ Failed to process data: {str(e)}")

# Test 6: High Risk Entities
print("\n[Test 6] Getting High Risk Entities...")
try:
    processor = MLDataProcessor(data_dir='../Hackathon_Nitro')
    processor.load_all_datasets()
    risks = processor.get_high_risk_entities()
    
    print(f"✓ High Risk Farmers: {len(risks.get('high_risk_farmers', []))}")
    print(f"✓ High Risk Dealers: {len(risks.get('high_risk_dealers', []))}")
    
    if risks.get('high_risk_farmers'):
        print("\n  Top 5 High Risk Farmers:")
        for farmer in risks['high_risk_farmers'][:5]:
            print(f"    - {farmer['farmer_id']}: {farmer['fraud_count']} fraud cases")
    
except Exception as e:
    print(f"✗ Failed to get high risk entities: {str(e)}")

# Test 7: Generate Report
print("\n[Test 7] Generating Comprehensive Report...")
try:
    processor = MLDataProcessor(data_dir='../Hackathon_Nitro')
    report = processor.generate_comprehensive_report(output_path='ml_test_report.json')
    print(f"✓ Report generated successfully")
    print(f"✓ Report saved to: ml_test_report.json")
    print(f"\nReport Summary:")
    print(f"  - Fraud Summary: {len(report.get('fraud_summary', {}))} metrics")
    print(f"  - Farmer Analysis: {len(report.get('farmer_analysis', {}))} metrics")
    print(f"  - Dealer Analysis: {len(report.get('dealer_analysis', {}))} metrics")
    
except Exception as e:
    print(f"✗ Failed to generate report: {str(e)}")

print("\n" + "="*60)
print("ML INTEGRATION TEST COMPLETED")
print("="*60)

# Save sample test results
print("\n[Saving] Sample test results to ml_test_output.json...")
try:
    test_results = {
        "test_timestamp": str(datetime.datetime.now()),
        "statistics": stats,
        "seasonal_recommendations": recommendations,
        "sample_prediction": result,
        "fraud_summary": fraud_summary,
        "high_risk_entities": risks
    }
    
    with open('ml_test_output.json', 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print("✓ Test results saved to ml_test_output.json")
except Exception as e:
    print(f"✗ Failed to save test results: {str(e)}")

print("\n✓ All tests completed! Check ml_test_output.json for detailed results.")
