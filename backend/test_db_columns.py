#!/usr/bin/env python3
"""Test if decision_makers column exists and is writable"""

import os
import asyncio
from dotenv import load_dotenv
from supabase_db import SupabaseDB

load_dotenv()

async def test_decision_makers_column():
    print("Testing decision_makers column...")
    print()

    db = SupabaseDB()

    # Get first lead
    print("1. Fetching a lead...")
    response = db.supabase.table('leads').select('*').limit(1).execute()

    if not response.data:
        print("❌ No leads found in database")
        return

    lead = response.data[0]
    lead_id = lead['id']
    print(f"✅ Got lead: {lead_id} - {lead.get('company_name')}")
    print()

    # Check if decision_makers column exists
    print("2. Checking if decision_makers column exists...")
    if 'decision_makers' in lead:
        print(f"✅ decision_makers column EXISTS (current value: {lead.get('decision_makers')})")
    else:
        print("❌ decision_makers column NOT FOUND in response")
        print(f"   Available columns: {list(lead.keys())}")
        return
    print()

    # Try to update decision_makers
    print("3. Attempting to write test data to decision_makers...")
    test_data = [
        {
            "name": "Test Contact",
            "title": "Test Title",
            "email": "test@test.com",
            "confidence": 0.95
        }
    ]

    try:
        update_response = db.supabase.table('leads').update({
            'decision_makers': test_data,
            'email_pattern': '{first}@test.com'
        }).eq('id', lead_id).execute()

        print(f"✅ Update successful!")
        print()

        # Verify it was saved
        print("4. Verifying data was saved...")
        verify_response = db.supabase.table('leads').select('id, company_name, decision_makers, email_pattern').eq('id', lead_id).execute()

        if verify_response.data:
            saved_lead = verify_response.data[0]
            dm = saved_lead.get('decision_makers', [])
            pattern = saved_lead.get('email_pattern')

            print(f"✅ Data verified!")
            print(f"   decision_makers: {len(dm) if isinstance(dm, list) else 'NOT A LIST'} contacts")
            print(f"   email_pattern: {pattern}")

            if dm:
                print(f"   First contact: {dm[0]}")
        else:
            print("❌ Could not verify - lead not found")

    except Exception as e:
        print(f"❌ Update failed: {e}")

asyncio.run(test_decision_makers_column())
