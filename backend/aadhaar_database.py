"""
Aadhaar Database System
Creates and manages Aadhaar records with land ownership information
"""

from sqlalchemy import Column, String, Integer, Float, Date, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from database import Base, engine, SessionLocal
from datetime import datetime, date
import random

class AadhaarRecord(Base):
    __tablename__ = "aadhaar_records"
    
    # Primary Identity Fields
    aadhaar_number = Column(String(12), primary_key=True, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)  # Male, Female, Other
    
    # Contact Information
    mobile_number = Column(String(10), nullable=False)
    email = Column(String(100), nullable=True)
    
    # Address Details
    address = Column(String(500), nullable=False)
    village = Column(String(100), nullable=True)
    district = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(6), nullable=False)
    
    # Land Ownership Information
    total_land_acres = Column(Float, default=0.0, nullable=False)
    
    # System Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    verified = Column(Boolean, default=True)


def create_aadhaar_tables():
    """Create Aadhaar database tables"""
    print("Creating Aadhaar database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Aadhaar tables created successfully!")


def generate_aadhaar_number():
    """Generate a random 12-digit Aadhaar number"""
    return ''.join([str(random.randint(0, 9)) for _ in range(12)])


def generate_sample_data(num_records=100):
    """Generate sample Aadhaar records with varied land ownership"""
    
    db = SessionLocal()
    
    # Sample data pools
    male_names = [
        "Rajesh Kumar", "Suresh Reddy", "Ramesh Naidu", "Venkatesh Rao", "Prakash Singh",
        "Mahesh Sharma", "Dinesh Patel", "Anil Verma", "Vijay Gupta", "Sanjay Joshi",
        "Ravi Kumar", "Ashok Reddy", "Mohan Naidu", "Krishna Rao", "Ganesh Singh",
        "Kiran Patel", "Deepak Sharma", "Rakesh Verma", "Santosh Gupta", "Manoj Joshi",
        "Naresh Kumar", "Pavan Reddy", "Srikanth Naidu", "Balaji Rao", "Harish Singh",
        "Naveen Patel", "Satish Sharma", "Ramakrishna Verma", "Venkateswara Rao", "Shankar Reddy"
    ]
    
    female_names = [
        "Lakshmi Devi", "Saraswati Bai", "Parvati Reddy", "Durga Rani", "Radha Kumari",
        "Sita Devi", "Gita Bai", "Meera Reddy", "Savitri Rani", "Kamala Kumari",
        "Sunita Devi", "Anjali Reddy", "Priya Rani", "Kavita Kumari", "Nirmala Devi",
        "Shanti Bai", "Usha Reddy", "Madhuri Rani", "Asha Kumari", "Pushpa Devi",
        "Vanaja Bai", "Bhavani Reddy", "Lalita Rani", "Manjula Kumari", "Padma Devi"
    ]
    
    villages = [
        "Ramapuram", "Venkatapur", "Krishna Nagar", "Sai Colony", "Gandhi Nagar",
        "Ambedkar Colony", "Nehru Nagar", "Subhash Nagar", "Rajiv Nagar", "Indira Colony",
        "Raghavendra Colony", "Srinivasa Nagar", "Lakshmi Nagar", "Durga Colony", "Kalpana Village"
    ]
    
    states_districts = [
        ("Andhra Pradesh", "Guntur"),
        ("Andhra Pradesh", "Krishna"),
        ("Andhra Pradesh", "Visakhapatnam"),
        ("Telangana", "Hyderabad"),
        ("Telangana", "Warangal"),
        ("Telangana", "Karimnagar"),
        ("Karnataka", "Bangalore Rural"),
        ("Karnataka", "Mysore"),
        ("Karnataka", "Belgaum"),
        ("Tamil Nadu", "Coimbatore"),
        ("Tamil Nadu", "Madurai"),
        ("Maharashtra", "Pune"),
        ("Maharashtra", "Nashik"),
    ]
    
    print(f"\nGenerating {num_records} Aadhaar records...")
    
    records_added = 0
    
    # Generate records with different land ownership scenarios
    for i in range(num_records):
        try:
            # Randomly decide if person has land (30% have land, 70% don't)
            has_land = random.random() < 0.3
            
            # Generate basic info
            is_male = random.random() < 0.6
            name = random.choice(male_names if is_male else female_names)
            gender = "Male" if is_male else "Female"
            
            # Generate age between 18 and 75
            age = random.randint(18, 75)
            dob = date(2025 - age, random.randint(1, 12), random.randint(1, 28))
            
            # Location
            state, district = random.choice(states_districts)
            village = random.choice(villages)
            
            # Land details - only acres
            if has_land:
                # Land between 0.5 to 20 acres
                total_land = round(random.uniform(0.5, 20.0), 2)
            else:
                total_land = 0.0
            
            # Create record
            record = AadhaarRecord(
                aadhaar_number=generate_aadhaar_number(),
                name=name,
                date_of_birth=dob,
                gender=gender,
                mobile_number=''.join([str(random.randint(0, 9)) for _ in range(10)]),
                email=f"{name.lower().replace(' ', '.')}@example.com" if random.random() < 0.4 else None,
                address=f"H.No. {random.randint(1, 500)}, {village}",
                village=village,
                district=district,
                state=state,
                pincode=''.join([str(random.randint(0, 9)) for _ in range(6)]),
                total_land_acres=total_land,
                verified=True,
                is_active=True
            )
            
            db.add(record)
            records_added += 1
            
            if (i + 1) % 20 == 0:
                db.commit()
                print(f"  Added {i + 1}/{num_records} records...")
                
        except Exception as e:
            print(f"  Error adding record {i + 1}: {e}")
            db.rollback()
            continue
    
    db.commit()
    print(f"\n✓ Successfully added {records_added} Aadhaar records!")
    
    # Show statistics
    print("\n" + "="*60)
    print("AADHAAR DATABASE STATISTICS")
    print("="*60)
    
    total = db.query(AadhaarRecord).count()
    with_land = db.query(AadhaarRecord).filter(AadhaarRecord.total_land_acres > 0).count()
    without_land = db.query(AadhaarRecord).filter(AadhaarRecord.total_land_acres == 0).count()
    
    print(f"Total Records: {total}")
    print(f"People with Land: {with_land} ({with_land*100/total:.1f}%)")
    print(f"People without Land: {without_land} ({without_land*100/total:.1f}%)")
    
    # Land statistics
    from sqlalchemy import func
    total_land = db.query(func.sum(AadhaarRecord.total_land_acres)).scalar() or 0
    
    avg_land = db.query(func.avg(AadhaarRecord.total_land_acres)).filter(
        AadhaarRecord.total_land_acres > 0
    ).scalar() or 0
    
    print(f"\nTotal Land Holdings: {total_land:.2f} acres")
    print(f"Average Land (landowners): {avg_land:.2f} acres")
    
    # Show sample records without land
    print("\n" + "="*60)
    print("SAMPLE RECORDS - PEOPLE WITHOUT LAND")
    print("="*60)
    
    no_land_samples = db.query(AadhaarRecord).filter(
        AadhaarRecord.total_land_acres == 0
    ).limit(10).all()
    
    for record in no_land_samples:
        print(f"\n{record.name} ({record.aadhaar_number})")
        print(f"  Location: {record.village}, {record.district}, {record.state}")
        print(f"  Land Ownership: 0 acres (No Land)")
    
    # Show sample records with land
    print("\n" + "="*60)
    print("SAMPLE RECORDS - PEOPLE WITH LAND")
    print("="*60)
    
    with_land_samples = db.query(AadhaarRecord).filter(
        AadhaarRecord.total_land_acres > 0
    ).limit(10).all()
    
    for record in with_land_samples:
        print(f"\n{record.name} ({record.aadhaar_number})")
        print(f"  Location: {record.village}, {record.district}, {record.state}")
        print(f"  Total Land: {record.total_land_acres} acres")
    
    db.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("AADHAAR DATABASE CREATION SYSTEM")
    print("="*60)
    
    # Create tables
    create_aadhaar_tables()
    
    # Generate sample data
    num_records = int(input("\nHow many Aadhaar records to generate? (default 100): ") or "100")
    generate_sample_data(num_records)
    
    print("\n✓ Aadhaar database setup complete!")
    print("="*60)
