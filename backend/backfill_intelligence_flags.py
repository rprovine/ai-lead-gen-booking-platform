"""
Backfill has_intelligence flags for leads that already have intelligence data
"""
import os
import asyncio
from supabase import create_client
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

async def backfill_intelligence_flags():
    """Update has_intelligence flag for all leads that have intelligence data"""

    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("🔍 Finding leads with intelligence data...")

    # Get all intelligence records
    intelligence_response = client.table('lead_intelligence').select('lead_id').execute()

    if not intelligence_response.data:
        print("No intelligence records found")
        return

    # Get unique lead IDs that have intelligence
    lead_ids_with_intelligence = list(set([record['lead_id'] for record in intelligence_response.data]))

    print(f"Found {len(lead_ids_with_intelligence)} leads with intelligence data")

    # Update each lead
    updated_count = 0
    for lead_id in lead_ids_with_intelligence:
        try:
            # Check if already has flag set
            lead_response = client.table('leads').select('has_intelligence').eq('id', lead_id).execute()

            if lead_response.data and not lead_response.data[0].get('has_intelligence'):
                # Update the lead
                client.table('leads').update({
                    'has_intelligence': True,
                    'intelligence_generated_at': datetime.now().isoformat()
                }).eq('id', lead_id).execute()

                updated_count += 1
                print(f"✓ Updated {lead_id}")
            else:
                print(f"⊘ Skipped {lead_id} (already has flag)")

        except Exception as e:
            print(f"✗ Error updating {lead_id}: {e}")

    print(f"\n✅ Backfill complete! Updated {updated_count} leads")

if __name__ == '__main__':
    asyncio.run(backfill_intelligence_flags())
