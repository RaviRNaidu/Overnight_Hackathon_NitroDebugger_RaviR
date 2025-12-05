"""
Script to delete all applications except those with RISK (high risk) fraud predictions.

This script:
1. Fetches all applications from database
2. Gets ML fraud prediction for each application
3. Deletes applications with SAFE (low risk) status
4. Keeps only RISK (high risk) applications
"""

from database import SessionLocal, Application
from ml_integrated_fraud_detector import get_ml_integrated_detector
import sys

def delete_non_high_risk_applications():
    """Delete all applications except RISK (high risk) ones"""
    db = SessionLocal()
    
    try:
        # Get all applications
        applications = db.query(Application).all()
        total_count = len(applications)
        
        if total_count == 0:
            print("\n❌ No applications found in database.")
            return
        
        print(f"\n📊 Found {total_count} applications in database")
        print("="*80)
        
        # Initialize ML fraud detector
        print("\n🔄 Initializing ML fraud detector...")
        ml_detector = get_ml_integrated_detector()
        
        high_risk_apps = []
        to_delete = []
        
        print("\n🔍 Analyzing fraud risk for each application...\n")
        
        for app in applications:
            # Create application data for ML prediction
            app_data = {
                'application_id': app.application_id,
                'farmer_name': app.farmer_name,
                'aadhaar_number': app.aadhaar_number,
                'mobile_number': app.mobile_number,
                'state': app.state,
                'district': app.district,
                'total_land_acres': app.total_land_acres,
                'crop_type': app.crop_type,
                'fertilizer_qty': app.fertilizer_qty,
                'seed_qty': app.seed_qty
            }
            
            # Get ML prediction
            try:
                prediction = ml_detector.predict_fraud(app_data)
                risk_level = prediction.get('risk_level', 'UNKNOWN')
                fraud_score = prediction.get('fraud_score', 0)
                
                print(f"  App {app.application_id} | {app.farmer_name:30s} | Risk: {risk_level:8s} | Score: {fraud_score:.2f}")
                
                # Keep RISK (high risk) applications, delete SAFE (low risk) applications
                if risk_level == 'RISK':
                    high_risk_apps.append({
                        'app': app,
                        'prediction': prediction
                    })
                else:
                    to_delete.append({
                        'app': app,
                        'prediction': prediction
                    })
                    
            except Exception as e:
                print(f"  ⚠️  Error predicting for {app.application_id}: {e}")
                # If prediction fails, add to delete list (safer to remove if we can't assess risk)
                to_delete.append({
                    'app': app,
                    'prediction': {'risk_level': 'ERROR', 'fraud_score': 0}
                })
        
        print("\n" + "="*80)
        print(f"\n📈 Risk Analysis Summary:")
        print(f"   Total Applications: {total_count}")
        print(f"   🔴 RISK - High Risk (to keep): {len(high_risk_apps)}")
        print(f"   🟢 SAFE - Low Risk (to delete): {len(to_delete)}")
        
        if len(high_risk_apps) > 0:
            print(f"\n✅ Applications to KEEP (RISK - High Risk):")
            for item in high_risk_apps:
                app = item['app']
                pred = item['prediction']
                print(f"   • {app.application_id} - {app.farmer_name} - Score: {pred.get('fraud_score', 0):.2f}")
        
        if len(to_delete) == 0:
            print(f"\n✅ No applications to delete. All are HIGH risk.")
            return
        
        print(f"\n⚠️  Applications to DELETE (SAFE - Low Risk):")
        for item in to_delete[:10]:  # Show first 10
            app = item['app']
            pred = item['prediction']
            print(f"   • {app.application_id} - {app.farmer_name} - Risk: {pred.get('risk_level', 'N/A')}")
        
        if len(to_delete) > 10:
            print(f"   ... and {len(to_delete) - 10} more")
        
        # Confirm deletion
        print(f"\n{'='*80}")
        print(f"⚠️  WARNING: This will DELETE {len(to_delete)} SAFE (low risk) applications!")
        print(f"Only {len(high_risk_apps)} RISK (high risk) applications will remain.")
        print(f"{'='*80}\n")
        
        confirm = input("Type 'DELETE' to confirm deletion: ")
        
        if confirm != 'DELETE':
            print("\n❌ Deletion cancelled.")
            return
        
        # Delete applications
        print(f"\n🗑️  Deleting {len(to_delete)} applications...")
        deleted_count = 0
        
        for item in to_delete:
            try:
                db.delete(item['app'])
                deleted_count += 1
            except Exception as e:
                print(f"   ⚠️  Error deleting {item['app'].application_id}: {e}")
        
        # Commit changes
        db.commit()
        
        print(f"\n✅ Successfully deleted {deleted_count} applications!")
        print(f"✅ {len(high_risk_apps)} RISK (high risk) applications remain in database.")
        
        # Verify deletion
        remaining = db.query(Application).count()
        print(f"\n📊 Final count: {remaining} applications in database")
        
        if remaining == len(high_risk_apps):
            print("✅ Verification passed: Count matches expected RISK applications.")
        else:
            print(f"⚠️  Warning: Expected {len(high_risk_apps)}, but found {remaining}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  DELETE LOW-RISK (SAFE) APPLICATIONS")
    print("  This script will remove all SAFE (low risk) applications")
    print("  Only RISK (high risk) fraud applications will be kept")
    print("="*80)
    
    delete_non_high_risk_applications()
    
    print("\n✅ Script completed.\n")
