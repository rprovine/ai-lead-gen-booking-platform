#!/usr/bin/env python3
"""
Test script for HubSpot CRM integration
Run this after adding your HUBSPOT_API_KEY to .env
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

import httpx

async def test_hubspot_integration():
    """Test sending a lead to HubSpot"""

    print("\n" + "="*80)
    print("TESTING HUBSPOT INTEGRATION")
    print("="*80 + "\n")

    # Check if HubSpot API key is configured
    hubspot_key = os.getenv('HUBSPOT_API_KEY')
    if not hubspot_key or hubspot_key == 'your_key_here':
        print("❌ HUBSPOT_API_KEY not configured in .env file")
        print("\nTo set up HubSpot integration:")
        print("1. Go to https://app.hubspot.com/settings/account/integrations/api-keys")
        print("2. Create a new API key")
        print("3. Add it to your .env file: HUBSPOT_API_KEY=your_actual_key")
        print("4. Restart the backend server")
        return

    print(f"✓ HubSpot API key configured: {hubspot_key[:15]}...")
    print()

    # First, get a list of leads to test with
    async with httpx.AsyncClient() as client:
        try:
            print("Fetching available leads...")
            response = await client.get("http://localhost:8000/api/leads")

            if response.status_code != 200:
                print(f"❌ Failed to fetch leads: {response.status_code}")
                print(f"Response: {response.text}")
                return

            leads = response.json()

            if not leads:
                print("❌ No leads found in database")
                print("\nCreate a lead first by running:")
                print('curl -s -X POST "http://localhost:8000/api/leads/discover" \\')
                print('  -H "Content-Type: application/json" \\')
                print('  -d \'{"industry":"Tourism","location":"Maui","min_employees":1,"max_results":1}\'')
                return

            print(f"✓ Found {len(leads)} leads")
            print()

            # Use the first lead for testing
            test_lead = leads[0]
            lead_id = test_lead.get('id')
            company_name = test_lead.get('company_name', 'Unknown')

            print(f"Testing with lead: {company_name}")
            print(f"Lead ID: {lead_id}")
            print()

            # Check if intelligence data exists
            intel_response = await client.get(f"http://localhost:8000/api/leads/{lead_id}")
            lead_data = intel_response.json()

            has_intelligence = lead_data.get('intelligence') is not None
            print(f"Intelligence data available: {'✓ Yes' if has_intelligence else '❌ No'}")

            if not has_intelligence:
                print("\nGenerating intelligence for better HubSpot sync...")
                intel_gen_response = await client.post(
                    f"http://localhost:8000/api/leads/{lead_id}/intelligence"
                )
                if intel_gen_response.status_code == 200:
                    print("✓ Intelligence generated successfully")
                else:
                    print(f"⚠ Warning: Could not generate intelligence: {intel_gen_response.status_code}")

            print()
            print("-" * 80)
            print("SENDING LEAD TO HUBSPOT...")
            print("-" * 80)
            print()

            # Send lead to HubSpot
            hubspot_response = await client.post(
                f"http://localhost:8000/api/leads/{lead_id}/send-to-hubspot"
            )

            if hubspot_response.status_code == 200:
                result = hubspot_response.json()
                print("✅ SUCCESS! Lead sent to HubSpot")
                print()
                print(f"HubSpot Company ID: {result.get('hubspot_company_id')}")
                print(f"HubSpot Contact ID: {result.get('hubspot_contact_id')}")
                print()
                print(f"View in HubSpot: {result.get('hubspot_url')}")
                print()
                print("Data synced:")
                print("  ✓ Company created with lead details")
                if result.get('hubspot_contact_id'):
                    print("  ✓ Contact created for decision maker")
                if has_intelligence:
                    print("  ✓ AI intelligence added as engagement note")
                print("  ✓ Lead marked as synced in database")

            elif hubspot_response.status_code == 503:
                print("❌ HubSpot integration not configured")
                print(hubspot_response.json())

            elif hubspot_response.status_code == 404:
                print(f"❌ Lead not found: {lead_id}")

            else:
                print(f"❌ Error: {hubspot_response.status_code}")
                print(hubspot_response.json())

        except httpx.ConnectError:
            print("❌ Cannot connect to backend server")
            print("\nMake sure the backend is running:")
            print("  cd /Users/renoprovine/Development/ai-lead-gen-booking-platform/backend")
            print("  source venv/bin/activate")
            print("  uvicorn main:app --reload")

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()

    print()
    print("="*80)
    print()

if __name__ == "__main__":
    asyncio.run(test_hubspot_integration())
