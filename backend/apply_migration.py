#!/usr/bin/env python3
"""
Apply database migration to add decision_makers column

This script reads the migration SQL file and applies it to your Supabase database.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Read migration SQL
migration_file = "migrations/add_decision_makers_column.sql"
with open(migration_file, 'r') as f:
    migration_sql = f.read()

print("=" * 70)
print("DATABASE MIGRATION: Add decision_makers column to leads table")
print("=" * 70)
print()

# Get Supabase credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("❌ ERROR: Supabase credentials not found in .env")
    print()
    print("Please set the following environment variables:")
    print("  SUPABASE_URL=your_supabase_project_url")
    print("  SUPABASE_KEY=your_supabase_service_key")
    print()
    print("Or run this SQL manually in your Supabase SQL Editor:")
    print()
    print("-" * 70)
    print(migration_sql)
    print("-" * 70)
    exit(1)

print(f"📊 Supabase URL: {supabase_url}")
print()
print("⚠️  IMPORTANT: Supabase Python client doesn't support raw SQL execution")
print("   via the REST API. You need to run this migration manually.")
print()
print("📋 Instructions:")
print()
print("1. Go to your Supabase project: https://supabase.com/dashboard")
print(f"2. Open your project (URL: {supabase_url})")
print("3. Click on 'SQL Editor' in the left sidebar")
print("4. Click 'New query'")
print("5. Copy and paste the SQL below:")
print()
print("-" * 70)
print(migration_sql)
print("-" * 70)
print()
print("6. Click 'Run' (or press Cmd/Ctrl + Enter)")
print("7. You should see 'Success. No rows returned'")
print()
print("✅ After running the migration, contacts will be saved to lead records!")
print()
