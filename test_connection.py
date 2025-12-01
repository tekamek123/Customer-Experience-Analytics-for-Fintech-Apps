"""
Quick test script to verify PostgreSQL connection
Run this before setting up the database
"""

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def test_connection():
    """Test PostgreSQL connection."""
    print("=" * 60)
    print("PostgreSQL Connection Test")
    print("=" * 60)
    
    # Get connection parameters
    db_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
    }
    
    print(f"\nConnection parameters:")
    print(f"  Host: {db_params['host']}")
    print(f"  Port: {db_params['port']}")
    print(f"  User: {db_params['user']}")
    print(f"  Password: {'*' * len(db_params['password'])}")
    
    # Test 1: Connect to default postgres database
    print("\n[Test 1] Connecting to PostgreSQL server...")
    try:
        conn = psycopg2.connect(
            database='postgres',  # Connect to default database
            **db_params
        )
        print("✓ Successfully connected to PostgreSQL server!")
        
        # Test 2: Check PostgreSQL version
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"\n[Test 2] PostgreSQL version:")
        print(f"  {version.split(',')[0]}")
        
        # Test 3: Check if bank_reviews database exists
        cursor.execute("""
            SELECT 1 FROM pg_database WHERE datname = 'bank_reviews'
        """)
        db_exists = cursor.fetchone()
        
        if db_exists:
            print("\n[Test 3] Database 'bank_reviews' exists")
            
            # Test 4: Connect to bank_reviews database
            cursor.close()
            conn.close()
            
            print("\n[Test 4] Connecting to 'bank_reviews' database...")
            conn = psycopg2.connect(
                database='bank_reviews',
                **db_params
            )
            print("✓ Successfully connected to 'bank_reviews' database!")
            
            # Test 5: Check tables
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            
            if tables:
                print(f"\n[Test 5] Found {len(tables)} table(s):")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("\n[Test 5] No tables found (database is empty)")
            
            cursor.close()
        else:
            print("\n[Test 3] Database 'bank_reviews' does not exist yet")
            print("  Run 'python database_setup.py' to create it")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("Connection test complete!")
        print("=" * 60)
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n✗ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if PostgreSQL service is running")
        print("   - Windows: Open Services (services.msc)")
        print("   - Look for 'postgresql-x64-16' or similar")
        print("2. Verify your password in .env file")
        print("3. Check if port 5432 is correct")
        print("4. Make sure PostgreSQL is installed correctly")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_connection()

