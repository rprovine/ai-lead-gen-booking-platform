#!/usr/bin/env python3
"""
Enrich all RESEARCHED leads with decision makers using Perplexity AI
"""

import asyncio
import sys
from dotenv import load_dotenv

load_dotenv()

from database import db as supabase_db

async def main():
    print("=" * 70)
    print("ENRICHING RESEARCHED LEADS WITH DECISION MAKERS")
    print("=" * 70)
    print()

    # Get all RESEARCHED leads
    print("1. Finding all RESEARCHED leads...")
    all_leads = await supabase_db.get_leads(limit=1000, status='RESEARCHED')

    # Filter for leads with 0 contacts
    leads_to_enrich = [l for l in all_leads if len(l.get('decision_makers', [])) == 0]

    if not leads_to_enrich:
        print("   ✅ All RESEARCHED leads already have contacts")
        print()
        return

    print(f"   Found {len(leads_to_enrich)} leads to enrich:")
    for lead in leads_to_enrich:
        print(f"   - {lead.get('company_name')}")
    print()

    # Enrich each lead
    print("2. Enriching leads with decision makers (using Perplexity AI)...")
    print()

    import aiohttp

    for i, lead in enumerate(leads_to_enrich, 1):
        lead_id = lead.get('id')
        company_name = lead.get('company_name')

        print(f"   [{i}/{len(leads_to_enrich)}] Enriching {company_name}...")

        try:
            # Call the intelligence endpoint with refresh=true to regenerate
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://localhost:8000/api/leads/{lead_id}/intelligence?refresh=true"
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Check if contacts were found
                        # We need to fetch the lead again to see updated decision_makers
                        updated_lead = await supabase_db.get_lead_by_id(lead_id)
                        dm_count = len(updated_lead.get('decision_makers', [])) if updated_lead else 0

                        if dm_count > 0:
                            print(f"      ✅ Found {dm_count} decision maker(s)")
                        else:
                            print(f"      ⚠️  No decision makers found")
                    else:
                        print(f"      ❌ Failed: {response.status}")
        except Exception as e:
            print(f"      ❌ Error: {e}")

        # Small delay to avoid rate limiting
        await asyncio.sleep(2)

    print()
    print("=" * 70)
    print("✅ ENRICHMENT COMPLETE!")
    print()

    # Show final summary
    all_leads = await supabase_db.get_leads(limit=1000, status='RESEARCHED')
    total_contacts = sum(len(l.get('decision_makers', [])) for l in all_leads)

    print(f"Summary:")
    print(f"  Total RESEARCHED leads: {len(all_leads)}")
    print(f"  Total decision makers found: {total_contacts}")
    print(f"  Avg contacts per lead: {total_contacts / len(all_leads) if all_leads else 0:.1f}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
