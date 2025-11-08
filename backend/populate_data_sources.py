#!/usr/bin/env python3
"""
Populate the data_sources_config table with default data sources
"""

import os
import asyncio
from dotenv import load_dotenv

# Load env BEFORE importing database
load_dotenv()

from database import db as supabase_db

async def populate_data_sources():
    """Insert default data source configurations"""

    data_sources = [
        {
            'organization_id': 'default',
            'source_type': 'anthropic',
            'source_name': 'Anthropic Claude AI',
            'is_enabled': False,
            'config': {
                'description': 'AI-powered lead intelligence and content generation',
                'docs_url': 'https://console.anthropic.com/',
                'required_fields': ['api_key']
            }
        },
        {
            'organization_id': 'default',
            'source_type': 'openai',
            'source_name': 'OpenAI',
            'is_enabled': False,
            'config': {
                'description': 'Embeddings and AI capabilities',
                'docs_url': 'https://platform.openai.com/api-keys',
                'required_fields': ['api_key']
            }
        },
        {
            'organization_id': 'default',
            'source_type': 'google_ai',
            'source_name': 'Google AI (Gemini)',
            'is_enabled': False,
            'config': {
                'description': 'Google Gemini AI models',
                'docs_url': 'https://makersuite.google.com/app/apikey',
                'required_fields': ['api_key']
            }
        },
        {
            'organization_id': 'default',
            'source_type': 'perplexity',
            'source_name': 'Perplexity AI',
            'is_enabled': False,
            'config': {
                'description': 'Real-time company research and intelligence',
                'docs_url': 'https://www.perplexity.ai/',
                'required_fields': ['api_key']
            }
        },
        {
            'organization_id': 'default',
            'source_type': 'apollo',
            'source_name': 'Apollo.io',
            'is_enabled': False,
            'config': {
                'description': 'Decision maker contact finder',
                'docs_url': 'https://apolloio.github.io/apollo-api-docs/',
                'required_fields': ['api_key']
            }
        },
        {
            'organization_id': 'default',
            'source_type': 'hunter',
            'source_name': 'Hunter.io',
            'is_enabled': False,
            'config': {
                'description': 'Email finder and verification',
                'docs_url': 'https://hunter.io/api-keys',
                'required_fields': ['api_key']
            }
        },
        {
            'organization_id': 'default',
            'source_type': 'rocketreach',
            'source_name': 'RocketReach',
            'is_enabled': False,
            'config': {
                'description': 'Executive contact data',
                'docs_url': 'https://rocketreach.co/api',
                'required_fields': ['api_key']
            }
        },
        {
            'organization_id': 'default',
            'source_type': 'serpapi',
            'source_name': 'SerpAPI',
            'is_enabled': False,
            'config': {
                'description': 'Google Maps and business data scraping',
                'docs_url': 'https://serpapi.com/',
                'required_fields': ['api_key']
            }
        },
        {
            'organization_id': 'default',
            'source_type': 'linkedin',
            'source_name': 'LinkedIn API',
            'is_enabled': False,
            'config': {
                'description': 'LinkedIn professional data access',
                'docs_url': 'https://developer.linkedin.com/',
                'required_fields': ['access_token']
            }
        },
        {
            'organization_id': 'default',
            'source_type': 'linkedin_sales_nav',
            'source_name': 'LinkedIn Sales Navigator',
            'is_enabled': False,
            'config': {
                'description': 'Advanced LinkedIn lead discovery',
                'docs_url': 'https://developer.linkedin.com/',
                'required_fields': ['api_key']
            }
        },
        {
            'organization_id': 'default',
            'source_type': 'hubspot',
            'source_name': 'HubSpot CRM',
            'is_enabled': False,
            'config': {
                'description': 'CRM integration for lead management',
                'docs_url': 'https://developers.hubspot.com/',
                'required_fields': ['api_key']
            }
        },
        {
            'organization_id': 'default',
            'source_type': 'sendgrid',
            'source_name': 'SendGrid Email',
            'is_enabled': False,
            'config': {
                'description': 'Email outreach automation',
                'docs_url': 'https://sendgrid.com/',
                'required_fields': ['api_key']
            }
        },
        {
            'organization_id': 'default',
            'source_type': 'twilio',
            'source_name': 'Twilio SMS',
            'is_enabled': False,
            'config': {
                'description': 'SMS outreach automation',
                'docs_url': 'https://www.twilio.com/',
                'required_fields': ['account_sid', 'auth_token', 'phone_number']
            }
        }
    ]

    print(f"📝 Inserting {len(data_sources)} data sources...")

    for source in data_sources:
        result = await supabase_db.upsert_data_source(source)
        if result:
            print(f"✅ {source['source_name']}")
        else:
            print(f"❌ Failed to insert {source['source_name']}")

    print("\n✨ Done! Checking results...")

    all_sources = await supabase_db.get_data_sources()
    print(f"📊 Total data sources in database: {len(all_sources)}")

if __name__ == "__main__":
    asyncio.run(populate_data_sources())
