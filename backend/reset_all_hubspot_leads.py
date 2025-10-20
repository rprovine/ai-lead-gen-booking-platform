#!/usr/bin/env python3
"""Reset all IN_HUBSPOT leads back to RESEARCHED for clean re-push"""

import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import db as supabase_db

async def main():
    print("=" * 70)
    print("RESET HUBSPOT LEADS TO RESEARCHED")
    print("=" * 70)
    print()

    # Get all leads with status IN_HUBSPOT
    print("1. Finding all leads with status IN_HUBSPOT...")
    all_leads = await supabase_db.get_leads(limit=1000)
    hubspot_leads = [l for l in all_leads if l.get('status') == 'IN_HUBSPOT']

    if not hubspot_leads:
        print("   ✅ No leads found with status IN_HUBSPOT")
        print()
        return

    print(f"   Found {len(hubspot_leads)} leads to reset:")
    for lead in hubspot_leads:
        dm_count = len(lead.get('decision_makers', []))
        print(f"   - {lead.get('company_name')} ({dm_count} contacts)")
    print()

    # Reset each one
    print("2. Resetting all to RESEARCHED status...")
    success_count = 0
    for lead in hubspot_leads:
        lead_id = lead.get('id')
        result = await supabase_db.update_lead(lead_id, {
            'status': 'RESEARCHED'
        })

        if result:
            success_count += 1
            dm_count = len(result.get('decision_makers', []))
            print(f"   ✅ {result.get('company_name')} → RESEARCHED ({dm_count} contacts)")
        else:
            print(f"   ❌ Failed to update {lead.get('company_name')}")

    print()
    print("=" * 70)
    print(f"✅ DONE! Reset {success_count}/{len(hubspot_leads)} leads to RESEARCHED")
    print()
    print("Next steps:")
    print("1. Refresh your frontend")
    print("2. Click 'HubSpot' button on any lead to push with new format")
    print("3. All contacts + source will be created in HubSpot!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
