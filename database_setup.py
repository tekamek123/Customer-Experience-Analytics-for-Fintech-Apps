"""
PostgreSQL Database Setup Script
Creates the database schema and sets up tables for bank reviews
"""

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Load environment variables if .env file exists
load_dotenv()


def get_db_connection(create_db=False):
    """
    Get database connection.
    
    Args:
        create_db: If True, connect to postgres database to create bank_reviews database
    
    Returns:
        Database connection object
    """
    # Database connection parameters
    # Can be set via environment variables or defaults
    db_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'database': 'postgres' if create_db else 'bank_reviews'
    }
    
    try:
        conn = psycopg2.connect(**db_params)
        if create_db:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        print("\nPlease ensure PostgreSQL is installed and running.")
        print("You may need to set environment variables:")
        print("  DB_HOST, DB_PORT, DB_USER, DB_PASSWORD")
        return None


def create_database():
    """Create the bank_reviews database if it doesn't exist."""
    conn = get_db_connection(create_db=True)
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("""
            SELECT 1 FROM pg_database WHERE datname = 'bank_reviews'
        """)
        
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(sql.SQL("CREATE DATABASE bank_reviews"))
            print("[OK] Database 'bank_reviews' created successfully")
        else:
            print("[OK] Database 'bank_reviews' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"[ERROR] Error creating database: {e}")
        conn.close()
        return False


def create_schema():
    """Create tables and indexes from schema file."""
    # Read schema file
    try:
        with open('database_schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
    except FileNotFoundError:
        print("[ERROR] Error: database_schema.sql file not found")
        return False
    
    conn = get_db_connection(create_db=False)
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Execute schema SQL
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in schema_sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for statement in statements:
            if statement:
                try:
                    cursor.execute(statement)
                    conn.commit()  # Commit after each successful statement
                except psycopg2.Error as e:
                    # Ignore "already exists" errors
                    if 'already exists' not in str(e).lower() and 'does not exist' not in str(e).lower():
                        print(f"  Warning: {e}")
                    conn.rollback()  # Rollback on error, then continue
        
        print("[OK] Database schema created successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"[ERROR] Error creating schema: {e}")
        conn.rollback()
        conn.close()
        return False


def main():
    """Main function to set up the database."""
    print("=" * 60)
    print("PostgreSQL Database Setup")
    print("=" * 60)
    
    # Step 1: Create database
    print("\n[Step 1/2] Creating database...")
    if not create_database():
        print("[ERROR] Failed to create database. Exiting.")
        return
    
    # Step 2: Create schema
    print("\n[Step 2/2] Creating schema...")
    if not create_schema():
        print("[ERROR] Failed to create schema. Exiting.")
        return
    
    print("\n" + "=" * 60)
    print("Database setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run insert_reviews.py to populate the database")
    print("2. Run verify_database.py to verify data integrity")


if __name__ == "__main__":
    main()

