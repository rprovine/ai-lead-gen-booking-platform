#!/usr/bin/env python3
"""
Apply data sources configuration table migration to Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Read the SQL migration file
with open('migrations/create_data_sources_table.sql', 'r') as f:
    sql = f.read()

# Connect to Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    exit(1)

print("=" * 70)
print("APPLYING DATA SOURCES CONFIGURATION TABLE MIGRATION")
print("=" * 70)
print(f"\n📊 Supabase URL: {supabase_url}\n")

# For Supabase, we need to use the PostgREST API or direct PostgreSQL connection
# The Python client doesn't support raw SQL, so we'll provide instructions

print("⚠️  The Supabase Python client doesn't support raw SQL execution.")
print("Please run this SQL manually in the Supabase SQL Editor:\n")
print("1. Go to https://supabase.com/dashboard")
print("2. Open your project")
print("3. Click 'SQL Editor' → 'New query'")
print("4. Copy and paste the SQL from:")
print("   migrations/create_data_sources_table.sql")
print("5. Click 'Run'\n")

print("Alternatively, connect via psql:")
print("=" * 70)
print(sql)
print("=" * 70)

# We can also try to execute via PostgreSQL connection if credentials are available
try:
    import psycopg2

    # Extract database connection details from SUPABASE_URL
    # Format: https://gxooanjnjiharjnnkqvm.supabase.co
    project_id = supabase_url.replace('https://', '').split('.')[0]

    db_password = os.getenv('SUPABASE_DB_PASSWORD')
    if db_password:
        conn_string = f"postgresql://postgres:{db_password}@db.{project_id}.supabase.co:5432/postgres"

        print("\n🔄 Attempting to apply migration via PostgreSQL...")
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        cursor.execute(sql)
        conn.commit()

        cursor.close()
        conn.close()

        print("✅ Migration applied successfully via PostgreSQL!")
    else:
        print("\n💡 Tip: Set SUPABASE_DB_PASSWORD in .env to auto-apply migrations")

except ImportError:
    print("\n💡 Install psycopg2 to auto-apply migrations: pip install psycopg2-binary")
except Exception as e:
    print(f"\n⚠️  Could not apply via PostgreSQL: {e}")
    print("Please apply manually using the SQL Editor.")
