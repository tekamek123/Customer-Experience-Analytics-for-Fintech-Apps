# Viewing Database in GUI (pgAdmin 4)

This guide shows you how to view your PostgreSQL database using pgAdmin 4, a graphical tool that comes with PostgreSQL.

## Step 1: Open pgAdmin 4

### Method 1: From Start Menu

1. Press `Win` key (Windows key)
2. Type "pgAdmin 4"
3. Click on "pgAdmin 4" application

### Method 2: From File Explorer

1. Navigate to: `C:\Program Files\PostgreSQL\18\pgAdmin 4\`
2. Double-click `pgAdmin4.exe`

### Method 3: From Command Line

```powershell
& "C:\Program Files\PostgreSQL\18\pgAdmin 4\bin\pgAdmin4.exe"
```

## Step 2: Connect to PostgreSQL Server

When pgAdmin opens:

1. **Enter Master Password** (first time only):

   - pgAdmin will ask you to set a master password
   - This is for pgAdmin itself, NOT your PostgreSQL password
   - Choose a password and remember it (or write it down)

2. **Add Server Connection**:

   - In the left panel, right-click on "Servers"
   - Select "Create" → "Server..."

3. **Fill in Connection Details**:

   - **General Tab**:

     - Name: `Local PostgreSQL` (or any name you prefer)

   - **Connection Tab**:
     - Host name/address: `localhost`
     - Port: `5432`
     - Maintenance database: `postgres`
     - Username: `postgres`
     - Password: **Enter your PostgreSQL password** (the one you set during installation)
     - Check "Save password" if you want (optional)

4. Click **"Save"**

## Step 3: Browse Your Database

Once connected:

1. **Expand the Server**:

   - Click the arrow next to "Local PostgreSQL" (or your server name)
   - Expand "Databases"
   - You should see `bank_reviews` database

2. **Open bank_reviews Database**:

   - Expand `bank_reviews`
   - Expand "Schemas"
   - Expand "public"
   - Expand "Tables"

3. **View Tables**:
   - You should see two tables:
     - `banks`
     - `reviews`

## Step 4: View Table Data

### View Banks Table:

1. Right-click on `banks` table
2. Select "View/Edit Data" → "All Rows"
3. You'll see all 3 banks with their IDs

### View Reviews Table:

1. Right-click on `reviews` table
2. Select "View/Edit Data" → "All Rows"
3. You'll see all 1,200 reviews!

**Note**: The reviews table has many rows, so it may take a moment to load.

### View Limited Rows:

1. Right-click on `reviews` table
2. Select "View/Edit Data" → "First 100 Rows"
3. This loads faster for large tables

## Step 5: Run SQL Queries

### Open Query Tool:

1. Right-click on `bank_reviews` database
2. Select "Query Tool"
3. A SQL editor will open

### Try These Queries:

**Count total reviews:**

```sql
SELECT COUNT(*) FROM reviews;
```

**View reviews by bank:**

```sql
SELECT b.bank_name, COUNT(r.review_id) as review_count
FROM banks b
LEFT JOIN reviews r ON b.bank_id = r.bank_id
GROUP BY b.bank_id, b.bank_name
ORDER BY review_count DESC;
```

**View average rating by bank:**

```sql
SELECT b.bank_name,
       ROUND(AVG(r.rating), 2) as avg_rating,
       COUNT(r.review_id) as review_count
FROM banks b
JOIN reviews r ON b.bank_id = r.bank_id
GROUP BY b.bank_id, b.bank_name
ORDER BY avg_rating DESC;
```

**View sample reviews:**

```sql
SELECT r.review_id, b.bank_name, r.rating, r.sentiment_label,
       LEFT(r.review_text, 100) as review_preview
FROM reviews r
JOIN banks b ON r.bank_id = b.bank_id
ORDER BY r.review_id
LIMIT 20;
```

**View sentiment distribution:**

```sql
SELECT sentiment_label, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reviews), 2) as percentage
FROM reviews
WHERE sentiment_label IS NOT NULL
GROUP BY sentiment_label
ORDER BY count DESC;
```

### Execute Query:

- Click the "Execute" button (play icon) or press `F5`
- Results will appear in the bottom panel

## Step 6: View Table Structure

### See Table Schema:

1. Right-click on a table (e.g., `reviews`)
2. Select "Properties"
3. Go to "Columns" tab to see all columns and their data types
4. Go to "Constraints" tab to see primary keys, foreign keys, etc.
5. Go to "Indexes" tab to see all indexes

## Troubleshooting

### Issue: "pgAdmin 4" not found

**Solution:**

- pgAdmin might not be installed
- Re-run PostgreSQL installer and make sure "pgAdmin 4" is checked
- Or download separately from: https://www.pgadmin.org/download/

### Issue: "Connection refused" or "Cannot connect"

**Solutions:**

1. Make sure PostgreSQL service is running:

   - Open Services (`Win + R` → `services.msc`)
   - Find "postgresql-x64-18" (or similar)
   - Ensure it's "Running"

2. Check your password:

   - Make sure you're using the PostgreSQL password, not pgAdmin master password

3. Check port:
   - Default is 5432
   - Verify in Services or PostgreSQL configuration

### Issue: "Master password" keeps asking

**Solution:**

- This is normal for pgAdmin security
- You can set it to be remembered, or just enter it each time
- This is different from your PostgreSQL password

### Issue: Can't see bank_reviews database

**Solution:**

- Make sure you ran `database_setup.py` or `create_tables.py`
- Refresh the server (right-click → Refresh)
- Check if database exists:
  ```sql
  SELECT datname FROM pg_database;
  ```

## Alternative: Using DBeaver (Free GUI Tool)

If pgAdmin doesn't work or you prefer another tool:

1. **Download DBeaver**: https://dbeaver.io/download/
2. **Install and open**
3. **Create new connection**:
   - Select "PostgreSQL"
   - Host: `localhost`
   - Port: `5432`
   - Database: `bank_reviews`
   - Username: `postgres`
   - Password: (your PostgreSQL password)
4. **Connect and browse** your tables

## Quick Reference

- **View Data**: Right-click table → "View/Edit Data" → "All Rows"
- **Run Query**: Right-click database → "Query Tool" → Type SQL → Execute (F5)
- **See Structure**: Right-click table → "Properties"
- **Refresh**: Right-click server/database → "Refresh"

## Visual Guide

```
pgAdmin 4 Interface:
┌─────────────────────────────────────┐
│  Servers (left panel)              │
│  └─ Local PostgreSQL               │
│     └─ Databases                    │
│        └─ bank_reviews              │
│           └─ Schemas                │
│              └─ public              │
│                 └─ Tables           │
│                    ├─ banks         │
│                    └─ reviews       │
└─────────────────────────────────────┘
```

Enjoy exploring your database! 🎉
