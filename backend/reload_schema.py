#!/usr/bin/env python3
"""
Reload Supabase schema cache to recognize new columns

This fixes the PGRST204 error: "Could not find the 'decision_makers' column of 'leads' in the schema cache"
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def reload_schema():
    """Reload PostgREST schema cache"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found in .env")
        return False

    print("=" * 70)
    print("RELOADING SUPABASE SCHEMA CACHE")
    print("=" * 70)
    print()

    # Method 1: Try to reload via PostgREST admin endpoint
    print("1. Attempting to reload PostgREST schema cache...")

    # PostgREST reload endpoint (if available)
    reload_url = f"{supabase_url}/rest/v1/rpc/reload_schema"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}"
    }

    try:
        response = requests.post(reload_url, headers=headers)
        if response.status_code == 200:
            print("   ✅ Schema cache reloaded successfully")
            return True
    except Exception as e:
        print(f"   ⚠️  reload_schema RPC not available: {e}")

    # Method 2: Execute a dummy query to force cache refresh
    print("\n2. Forcing cache refresh with dummy query...")

    try:
        # Query the leads table to force schema inspection
        query_url = f"{supabase_url}/rest/v1/leads?select=id,decision_makers&limit=1"
        response = requests.get(query_url, headers=headers)

        if response.status_code == 200:
            print("   ✅ Schema cache refreshed via query")
            print("   ✅ decision_makers column is now accessible")
            return True
        else:
            print(f"   ❌ Query failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = reload_schema()

    if success:
        print()
        print("=" * 70)
        print("✅ SUCCESS! Schema cache reloaded")
        print()
        print("Next steps:")
        print("1. Restart your backend server")
        print("2. Test the intelligence endpoint again")
        print("=" * 70)
    else:
        print()
        print("=" * 70)
        print("⚠️  MANUAL STEPS REQUIRED")
        print()
        print("Please go to Supabase Dashboard:")
        print("1. Open SQL Editor")
        print("2. Run: SELECT * FROM leads WHERE id = 'lead_c9078f63' LIMIT 1;")
        print("3. This will force the schema cache to refresh")
        print("4. Then restart your backend")
        print("=" * 70)
