"""
Database Migration Script
Adds review_comments, reviewed_by, and reviewed_at columns to applications table
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:6361@localhost:5432/farmer_portal")
engine = create_engine(DATABASE_URL)

def migrate():
    """Add review columns to applications table"""
    
    with engine.connect() as conn:
        try:
            # Check if columns exist
            print("Checking for existing columns...")
            
            # Add review_comments column
            try:
                conn.execute(text("""
                    ALTER TABLE applications 
                    ADD COLUMN IF NOT EXISTS review_comments TEXT
                """))
                print("✓ Added review_comments column")
            except Exception as e:
                print(f"review_comments column may already exist: {e}")
            
            # Add reviewed_by column
            try:
                conn.execute(text("""
                    ALTER TABLE applications 
                    ADD COLUMN IF NOT EXISTS reviewed_by VARCHAR(100)
                """))
                print("✓ Added reviewed_by column")
            except Exception as e:
                print(f"reviewed_by column may already exist: {e}")
            
            # Add reviewed_at column
            try:
                conn.execute(text("""
                    ALTER TABLE applications 
                    ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP
                """))
                print("✓ Added reviewed_at column")
            except Exception as e:
                print(f"reviewed_at column may already exist: {e}")
            
            conn.commit()
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            conn.rollback()

if __name__ == "__main__":
    print("Starting database migration...")
    migrate()
