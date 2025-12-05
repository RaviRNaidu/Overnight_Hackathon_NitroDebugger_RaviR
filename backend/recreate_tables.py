from database import engine, Base
from sqlalchemy import text

# Drop all existing tables
print("Dropping existing tables...")
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS applications CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS users CASCADE'))
    conn.commit()
print("Tables dropped successfully!")

# Recreate tables with updated schema
print("Creating tables with updated schema...")
Base.metadata.create_all(bind=engine)
print("Tables recreated successfully!")

# Recreate default users
from seed_users import create_database
import psycopg2

conn = psycopg2.connect(
    user="postgres",
    password="6361",
    host="localhost",
    port="5432",
    database="farmer_portal"
)
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO users (username, password, name, department) 
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (username) DO NOTHING
""", ('admin', 'admin123', 'Agriculture Admin', 'agriculture'))

cursor.execute("""
    INSERT INTO users (username, password, name, department) 
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (username) DO NOTHING
""", ('officer1', 'officer123', 'Agriculture Officer', 'agriculture'))

conn.commit()
cursor.close()
conn.close()

print("Default users created!")
print("\n✓ Database schema updated successfully!")
print("✓ application_id column expanded to 50 characters")
