"""
Quick setup script for Aadhaar database
"""

from aadhaar_database import create_aadhaar_tables, generate_sample_data

if __name__ == "__main__":
    print("\n" + "="*70)
    print("AADHAAR DATABASE QUICK SETUP")
    print("="*70)
    
    # Create tables
    create_aadhaar_tables()
    
    # Generate 150 sample records (about 70% without land, 30% with land)
    print("\nGenerating sample data...")
    generate_sample_data(num_records=150)
    
    print("\n" + "="*70)
    print("✓ SETUP COMPLETE!")
    print("="*70)
    print("\nYou can now:")
    print("  1. Search Aadhaar records via API: GET /api/aadhaar/search/{aadhaar_number}")
    print("  2. View landless people: GET /api/aadhaar/landless")
    print("  3. View landowners: GET /api/aadhaar/landowners")
    print("  4. Get statistics: GET /api/aadhaar/statistics")
    print("  5. Verify Aadhaar for application: POST /api/aadhaar/verify")
    print("="*70 + "\n")
