#!/usr/bin/env python3
"""Reset Pacific IT Support status to RESEARCHED for testing"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import db as supabase_db

async def main():
    lead_id = "lead_c9078f63"

    # Reset status to RESEARCHED
    result = await supabase_db.update_lead(lead_id, {
        'status': 'RESEARCHED'
    })

    if result:
        print(f"✅ Reset {result.get('company_name')} to status: RESEARCHED")
        print(f"   Now you can push to HubSpot again to test!")
    else:
        print(f"❌ Failed to update lead")

if __name__ == "__main__":
    asyncio.run(main())
