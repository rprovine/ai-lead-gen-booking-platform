#!/usr/bin/env python3
"""
Quick test script to demonstrate executive contact finding for Hawaiian Airlines
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from executive_finder import ExecutiveContactFinder

async def main():
    """Test executive finder with Hawaiian Airlines"""

    print("\n" + "="*80)
    print("TESTING EXECUTIVE CONTACT FINDER - Hawaiian Airlines")
    print("="*80 + "\n")

    finder = ExecutiveContactFinder()

    # Test with Hawaiian Airlines
    company_name = "Hawaiian Airlines"
    website = "https://www.hawaiianairlines.com"

    print(f"Company: {company_name}")
    print(f"Website: {website}\n")

    # Find decision makers
    result = await finder.find_decision_makers(
        company_name=company_name,
        website=website,
        industry="Airlines/Aviation",
        employee_count=7000
    )

    print("\n" + "="*80)
    print("RESULTS")
    print("="*80 + "\n")

    executives = result.get('executives', [])

    if executives:
        print(f"✓ Found {len(executives)} decision makers!\n")

        for i, exec_data in enumerate(executives, 1):
            print(f"{i}. {exec_data.get('name', 'N/A')}")
            print(f"   Title: {exec_data.get('title', 'N/A')}")
            print(f"   Email: {exec_data.get('email', 'N/A')}")
            print(f"   Phone: {exec_data.get('phone', 'N/A')}")
            print(f"   LinkedIn: {exec_data.get('linkedin', 'N/A')}")
            print(f"   Source: {exec_data.get('source', 'N/A')}")
            print(f"   Confidence: {exec_data.get('confidence', 'N/A')}")
            print()
    else:
        print("❌ No decision makers found")
        print("\nThis could mean:")
        print("- Apollo.io Basic plan may not have Hawaiian Airlines data")
        print("- The domain may not be in their database")
        print("- Try a tech company domain instead (e.g., microsoft.com)")
        print(f"\nDebug info: {result}")

if __name__ == "__main__":
    asyncio.run(main())
