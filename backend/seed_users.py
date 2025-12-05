"""
SQL script to insert initial admin user
"""
import psycopg2

DB_USER = "postgres"
DB_PASSWORD = "6361"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "farmer_portal"

try:
    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
    cursor = conn.cursor()
    
    # Insert default admin user
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
    
    # Insert government portal users
    cursor.execute("""
        INSERT INTO users (username, password, name, department) 
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (username) DO NOTHING
    """, ('gov_admin', 'gov@123', 'Government Administrator', 'government'))
    
    cursor.execute("""
        INSERT INTO users (username, password, name, department) 
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (username) DO NOTHING
    """, ('gov_officer', 'gov@456', 'Government Review Officer', 'government'))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("✅ Default users created successfully!")
    print("   Agriculture Department:")
    print("   - admin / admin123")
    print("   - officer1 / officer123")
    print("   Government Portal:")
    print("   - gov_admin / gov@123")
    print("   - gov_officer / gov@456")
    
except Exception as e:
    print(f"❌ Error: {e}")
