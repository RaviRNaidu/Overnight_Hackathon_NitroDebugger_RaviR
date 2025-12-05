"""
Drop and recreate Aadhaar tables with simplified schema
"""

from database import Base, engine
from aadhaar_database import AadhaarRecord
from sqlalchemy import inspect

if __name__ == "__main__":
    print("\n" + "="*70)
    print("RECREATING AADHAAR DATABASE TABLES")
    print("="*70)
    
    inspector = inspect(engine)
    
    # Check if table exists
    if 'aadhaar_records' in inspector.get_table_names():
        print("\nDropping existing aadhaar_records table...")
        AadhaarRecord.__table__.drop(engine)
        print("✓ Old table dropped")
    
    # Create new table with updated schema
    print("\nCreating new aadhaar_records table...")
    AadhaarRecord.__table__.create(engine)
    print("✓ New table created with simplified schema")
    
    print("\n" + "="*70)
    print("✓ MIGRATION COMPLETE!")
    print("="*70)
    print("\nYou can now run: python setup_aadhaar.py")
    print("="*70 + "\n")
