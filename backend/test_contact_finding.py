#!/usr/bin/env python3
"""
Test Contact Finding APIs

Verifies that Hunter.io, Apollo.io, and RocketReach are configured
and working correctly to find decision-maker contacts.
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from executive_finder import ExecutiveContactFinder


async def test_contact_finding():
    """Test contact finding for a sample company"""

    print("=" * 60)
    print("CONTACT FINDING API TEST")
    print("=" * 60)
    print()

    # Check which APIs are configured
    print("📋 Checking API Configuration:")
    print(f"  Hunter.io API Key: {'✅ Configured' if os.getenv('HUNTER_API_KEY') else '❌ Missing'}")
    print(f"  Apollo.io API Key: {'✅ Configured' if os.getenv('APOLLO_API_KEY') else '❌ Missing'}")
    print(f"  RocketReach API Key: {'✅ Configured' if os.getenv('ROCKETREACH_API_KEY') else '❌ Missing'}")
    print()

    if not any([os.getenv('HUNTER_API_KEY'), os.getenv('APOLLO_API_KEY'), os.getenv('ROCKETREACH_API_KEY')]):
        print("❌ No contact finding APIs configured!")
        print()
        print("Add to your .env file:")
        print("  HUNTER_API_KEY=your_hunter_key")
        print("  APOLLO_API_KEY=your_apollo_key")
        print("  ROCKETREACH_API_KEY=your_rocketreach_key")
        return

    # Initialize finder
    finder = ExecutiveContactFinder()

    # Test with a well-known Hawaii company
    print("🔍 Testing with sample company: Outrigger Hotels")
    print()

    try:
        result = await finder.find_decision_makers(
            company_name="Outrigger Hotels",
            website="outrigger.com",
            industry="Hospitality",
            employee_count=500
        )

        print("📊 RESULTS:")
        print(f"  Email Pattern: {result.get('email_pattern', 'Not found')}")
        print(f"  Company Domain: {result.get('company_domain', 'Not found')}")
        print()

        executives = result.get('executives', [])
        if executives:
            print(f"✅ Found {len(executives)} decision makers:")
            print()
            for i, exec in enumerate(executives[:5], 1):  # Show first 5
                print(f"  {i}. {exec.get('name', 'Unknown')}")
                print(f"     Title: {exec.get('title', 'Unknown')}")
                print(f"     Email: {exec.get('email', 'Not found')}")
                print(f"     Phone: {exec.get('phone', 'Not found')}")
                print(f"     LinkedIn: {exec.get('linkedin', 'Not found')}")
                print(f"     Confidence: {exec.get('confidence', 'Unknown')}")
                print()
        else:
            print("⚠️  No decision makers found")
            print()
            print("This could mean:")
            print("  1. API keys are invalid or expired")
            print("  2. Company domain not in API databases")
            print("  3. API rate limits reached")
            print()
            print("Try a different company or check your API keys")

    except Exception as e:
        print(f"❌ Error during contact finding: {e}")
        print()
        print("Check:")
        print("  1. API keys are valid")
        print("  2. Internet connection working")
        print("  3. API services are up")

    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_contact_finding())
