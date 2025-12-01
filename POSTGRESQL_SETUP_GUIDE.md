# PostgreSQL Setup and Testing Guide

This guide will help you install PostgreSQL and test Task 3 database implementation.

## Step 1: Install PostgreSQL

### For Windows:

1. **Download PostgreSQL:**
   - Go to https://www.postgresql.org/download/windows/
   - Click "Download the installer" from EnterpriseDB
   - Download the latest version (e.g., PostgreSQL 16.x)

2. **Run the Installer:**
   - Run the downloaded `.exe` file
   - Follow the installation wizard:
     - **Installation Directory**: Keep default (usually `C:\Program Files\PostgreSQL\16`)
     - **Select Components**: Keep all checked (PostgreSQL Server, pgAdmin 4, Stack Builder, Command Line Tools)
     - **Data Directory**: Keep default
     - **Password**: **IMPORTANT** - Set a password for the `postgres` superuser (remember this!)
     - **Port**: Keep default `5432`
     - **Advanced Options**: Keep default locale
   - Complete the installation

3. **Verify Installation:**
   - Open Command Prompt or PowerShell
   - Run: `psql --version`
   - You should see the PostgreSQL version number

### Alternative: Using Chocolatey (if you have it)
```powershell
choco install postgresql
```

## Step 2: Start PostgreSQL Service

### Check if PostgreSQL is Running:

1. **Using Services (GUI):**
   - Press `Win + R`, type `services.msc`, press Enter
   - Look for "postgresql-x64-16" (or similar)
   - Right-click → Start (if not running)

2. **Using Command Line:**
   ```powershell
   # Check status
   Get-Service -Name postgresql*
   
   # Start service (if not running)
   Start-Service -Name postgresql-x64-16
   ```

## Step 3: Configure Database Connection

1. **Create `.env` file in project root:**
   ```bash
   # In your project directory (week2)
   # Create a file named .env (no extension)
   ```

2. **Add database credentials to `.env`:**
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=your_postgres_password_here
   DB_NAME=bank_reviews
   ```
   
   **Replace `your_postgres_password_here` with the password you set during installation!**

3. **Verify `.env` file is in `.gitignore`:**
   - The `.env` file should already be in `.gitignore` to keep your password safe

## Step 4: Install Python Dependencies

```bash
# Make sure you're in the project directory
cd "D:\My Projects\Kifiya AI Mastery Training\week2"

# Install database libraries
pip install psycopg2-binary python-dotenv
```

## Step 5: Test Database Connection

### Quick Connection Test:

Create a test script `test_connection.py`:

```python
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        database='postgres'  # Connect to default postgres database first
    )
    print("✓ Successfully connected to PostgreSQL!")
    conn.close()
except Exception as e:
    print(f"✗ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check if PostgreSQL service is running")
    print("2. Verify your password in .env file")
    print("3. Check if port 5432 is correct")
```

Run it:
```bash
python test_connection.py
```

## Step 6: Set Up the Database

### Step 6.1: Create Database and Schema

```bash
python database_setup.py
```

**Expected Output:**
```
============================================================
PostgreSQL Database Setup
============================================================

[Step 1/2] Creating database...
✓ Database 'bank_reviews' created successfully

[Step 2/2] Creating schema...
✓ Database schema created successfully

============================================================
Database setup complete!
============================================================
```

**If you get errors:**
- **"password authentication failed"**: Check your `.env` file password
- **"could not connect to server"**: Make sure PostgreSQL service is running
- **"permission denied"**: Make sure you're using the `postgres` user or a user with CREATE DATABASE privileges

### Step 6.2: Insert Review Data

**Make sure you have the processed data files:**
- `data/processed/reviews_cleaned.csv` OR
- `data/processed/reviews_analyzed.csv` (preferred, has sentiment data)

If you don't have these files, run:
```bash
# First, scrape and preprocess (if not done)
python scrape_reviews.py
python preprocess_reviews.py

# Then run analysis (optional but recommended)
python analysis_pipeline.py
```

**Insert data:**
```bash
python insert_reviews.py
```

**Expected Output:**
```
============================================================
Inserting Reviews into PostgreSQL Database
============================================================

Loading analyzed reviews from data/processed/reviews_analyzed.csv...
✓ Loaded 1201 reviews

Processing banks...
  Created bank: Commercial Bank of Ethiopia (ID: 1)
  Created bank: Bank of Abyssinia (ID: 2)
  Created bank: Dashen Bank (ID: 3)

Preparing review data...

Inserting 1201 reviews...
✓ Successfully inserted 1201 reviews

============================================================
Data insertion complete!
============================================================
```

### Step 6.3: Verify Data Integrity

```bash
python verify_database.py
```

**Expected Output:**
```
============================================================
Database Verification Queries
============================================================

[Query 1] Total Reviews Count
------------------------------------------------------------
Total reviews in database: 1,201

[Query 2] Reviews Count by Bank
------------------------------------------------------------
Bank Name                                 Review Count
------------------------------------------------------------
Commercial Bank of Ethiopia                        400
Bank of Abyssinia                                  400
Dashen Bank                                        401

[Query 3] Average Rating by Bank
------------------------------------------------------------
...
```

## Step 7: Manual Database Inspection (Optional)

### Using psql Command Line:

```bash
# Connect to database
psql -U postgres -d bank_reviews

# Once connected, try these SQL commands:
SELECT COUNT(*) FROM reviews;
SELECT * FROM banks;
SELECT bank_name, COUNT(*) FROM reviews r JOIN banks b ON r.bank_id = b.bank_id GROUP BY bank_name;
\q  # Exit
```

### Using pgAdmin 4 (GUI):

1. **Open pgAdmin 4** (installed with PostgreSQL)
2. **Connect to server:**
   - Right-click "Servers" → "Create" → "Server"
   - Name: `Local PostgreSQL`
   - Connection tab:
     - Host: `localhost`
     - Port: `5432`
     - Username: `postgres`
     - Password: (your password)
3. **Browse database:**
   - Expand: Servers → Local PostgreSQL → Databases → bank_reviews
   - Right-click `bank_reviews` → "Query Tool"
   - Run: `SELECT COUNT(*) FROM reviews;`

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'psycopg2'"
**Solution:**
```bash
pip install psycopg2-binary
```

### Issue: "could not connect to server"
**Solutions:**
1. Check if PostgreSQL service is running:
   ```powershell
   Get-Service postgresql*
   ```
2. Start the service:
   ```powershell
   Start-Service postgresql-x64-16
   ```

### Issue: "password authentication failed"
**Solutions:**
1. Verify password in `.env` file matches PostgreSQL password
2. Try resetting PostgreSQL password:
   ```bash
   # Connect as postgres user
   psql -U postgres
   
   # In psql:
   ALTER USER postgres PASSWORD 'new_password';
   \q
   ```
3. Update `.env` file with new password

### Issue: "permission denied to create database"
**Solutions:**
1. Make sure you're using the `postgres` superuser
2. Or grant permissions:
   ```sql
   -- Connect as postgres user
   psql -U postgres
   
   -- Grant permissions
   ALTER USER your_username CREATEDB;
   ```

### Issue: "relation already exists"
**Solution:**
- This is normal if you run `database_setup.py` multiple times
- The script handles this gracefully
- If you want to start fresh:
  ```sql
  DROP DATABASE bank_reviews;
  ```
  Then run `database_setup.py` again

## Quick Test Checklist

- [ ] PostgreSQL installed and service running
- [ ] `.env` file created with correct credentials
- [ ] Python dependencies installed (`psycopg2-binary`, `python-dotenv`)
- [ ] `database_setup.py` runs successfully
- [ ] `insert_reviews.py` inserts 1,200+ reviews
- [ ] `verify_database.py` shows correct data counts
- [ ] Can query database manually (via psql or pgAdmin)

## Next Steps

Once everything is working:
1. ✅ Database is set up and populated
2. ✅ Data integrity verified
3. Ready for Task 4: Data Visualization and Reporting

## Additional Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- psycopg2 Documentation: https://www.psycopg.org/docs/
- pgAdmin Documentation: https://www.pgadmin.org/docs/

