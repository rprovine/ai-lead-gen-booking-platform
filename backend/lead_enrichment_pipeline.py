"""
Lead Enrichment Pipeline - Automated Contact & Intelligence Enrichment

Runs after lead discovery to:
1. Find decision-maker contacts (emails, phones, LinkedIn)
2. Run AI research (Perplexity + Claude)
3. Generate personalized sales playbooks
4. Prepare leads for HubSpot with complete intelligence

This happens BEFORE leads go to HubSpot, so they're ready to engage.
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import os
from database import db as supabase_db
from executive_finder import ExecutiveContactFinder
from perplexity_research import PerplexityResearcher
from sales_playbook_generator import SalesPlaybookPDFGenerator


class LeadEnrichmentPipeline:
    """
    Automates the enrichment of discovered leads with:
    - Decision-maker contacts
    - AI-powered research
    - Sales intelligence
    - Personalized playbooks
    """

    def __init__(self):
        self.contact_finder = ExecutiveContactFinder()
        self.researcher = PerplexityResearcher() if os.getenv('PERPLEXITY_API_KEY') else None
        self.playbook_generator = SalesPlaybookPDFGenerator()

    async def enrich_lead(self, lead: Dict) -> Dict:
        """
        Enrich a single lead with contacts and intelligence

        Args:
            lead: Lead dict with company_name, website, industry, etc.

        Returns:
            Enriched lead with:
            - decision_makers: List of contacts with emails/phones
            - research_summary: AI research about the company
            - pain_points: Identified pain points
            - talking_points: Personalized talking points
            - recommended_approach: How to engage
            - playbook_url: URL to generated sales playbook (optional)
        """
        company_name = lead.get('company_name', '')
        website = lead.get('website', '')
        industry = lead.get('industry', '')

        print(f"🔍 Enriching: {company_name}")

        enrichment = {
            'lead_id': lead.get('id'),
            'company_name': company_name,
            'enriched_at': datetime.now().isoformat(),
            'decision_makers': [],
            'research_summary': None,
            'pain_points': [],
            'talking_points': [],
            'recommended_approach': None,
            'playbook_url': None,
            'enrichment_status': 'in_progress'
        }

        # Step 1: Find decision-maker contacts
        print(f"  👤 Finding decision-makers...")
        try:
            contact_data = await self.contact_finder.find_decision_makers(
                company_name=company_name,
                website=website,
                industry=industry,
                employee_count=lead.get('employee_count')
            )

            enrichment['decision_makers'] = contact_data.get('executives', [])[:5]  # Top 5
            enrichment['email_pattern'] = contact_data.get('email_pattern')

            if enrichment['decision_makers']:
                print(f"    ✅ Found {len(enrichment['decision_makers'])} decision-makers")
            else:
                print(f"    ⚠️  No decision-makers found")

        except Exception as e:
            print(f"    ❌ Error finding contacts: {e}")

        # Step 2: AI Research (if Perplexity available)
        if self.researcher:
            print(f"  🤖 Running AI research...")
            try:
                research = await self.researcher.research_company(
                    company_name=company_name,
                    website=website,
                    industry=industry
                )

                enrichment['research_summary'] = research.get('summary', '')
                enrichment['pain_points'] = research.get('pain_points', [])
                enrichment['recent_news'] = research.get('recent_news', [])
                enrichment['tech_stack'] = research.get('tech_stack', [])

                print(f"    ✅ Research complete")

            except Exception as e:
                print(f"    ❌ Error in research: {e}")

        # Step 3: Generate talking points and approach
        print(f"  💡 Generating sales intelligence...")
        try:
            sales_intel = self._generate_sales_intelligence(
                lead=lead,
                decision_makers=enrichment['decision_makers'],
                research=enrichment.get('research_summary', ''),
                pain_points=enrichment.get('pain_points', [])
            )

            enrichment['talking_points'] = sales_intel['talking_points']
            enrichment['recommended_approach'] = sales_intel['recommended_approach']
            enrichment['value_proposition'] = sales_intel['value_proposition']

            print(f"    ✅ Sales intelligence generated")

        except Exception as e:
            print(f"    ❌ Error generating intelligence: {e}")

        # Step 4: Mark enrichment as complete
        enrichment['enrichment_status'] = 'completed'

        return enrichment

    async def enrich_batch(
        self,
        leads: List[Dict],
        max_concurrent: int = 3
    ) -> List[Dict]:
        """
        Enrich multiple leads concurrently (with rate limiting)

        Args:
            leads: List of lead dicts
            max_concurrent: Max concurrent enrichments (to avoid rate limits)

        Returns:
            List of enriched leads
        """
        print(f"\n📊 Enriching {len(leads)} leads (max {max_concurrent} concurrent)...")

        # Process in batches to avoid rate limits
        enriched_leads = []

        for i in range(0, len(leads), max_concurrent):
            batch = leads[i:i + max_concurrent]

            print(f"\n📦 Batch {i//max_concurrent + 1}: Processing {len(batch)} leads...")

            # Enrich batch concurrently
            tasks = [self.enrich_lead(lead) for lead in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle results and errors
            for lead, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    print(f"  ❌ Failed to enrich {lead.get('company_name')}: {result}")
                    enriched_leads.append({
                        'lead_id': lead.get('id'),
                        'enrichment_status': 'failed',
                        'error': str(result)
                    })
                else:
                    enriched_leads.append(result)

            # Small delay between batches to respect rate limits
            if i + max_concurrent < len(leads):
                await asyncio.sleep(2)

        return enriched_leads

    def _generate_sales_intelligence(
        self,
        lead: Dict,
        decision_makers: List[Dict],
        research: str,
        pain_points: List[str]
    ) -> Dict:
        """
        Generate personalized sales intelligence using AI + templates

        Returns:
            - talking_points: Key points to mention
            - recommended_approach: How to engage
            - value_proposition: Customized value prop
        """
        company_name = lead.get('company_name', '')
        industry = lead.get('industry', 'business')
        score = lead.get('score', 0)

        # Generate talking points based on ICP and research
        talking_points = []

        # Industry-specific talking points
        if 'hospitality' in industry.lower() or 'tourism' in industry.lower():
            talking_points.extend([
                "Guest experience optimization through AI",
                "Automated booking and reservation management",
                "Personalized guest recommendations",
                "Revenue optimization and dynamic pricing"
            ])
        elif 'healthcare' in industry.lower():
            talking_points.extend([
                "Patient experience and engagement automation",
                "Administrative task automation",
                "Appointment scheduling optimization",
                "Data-driven patient insights"
            ])
        elif 'retail' in industry.lower():
            talking_points.extend([
                "Customer experience personalization",
                "Inventory optimization",
                "Sales forecasting and demand planning",
                "Customer behavior analytics"
            ])
        else:
            talking_points.extend([
                "Business process automation",
                "Data-driven decision making",
                "Operational efficiency improvements",
                "Customer experience enhancement"
            ])

        # Add pain point-based talking points
        if pain_points:
            for pain in pain_points[:3]:  # Top 3 pain points
                talking_points.append(f"Solving: {pain}")

        # Recommended approach based on score and contacts
        if score >= 80:
            approach = "HIGH PRIORITY - Direct outreach"
            if decision_makers:
                primary_contact = decision_makers[0]
                approach += f" to {primary_contact.get('title', 'decision-maker')}"
            approach += ". Emphasize quick wins and ROI. Offer discovery call within 48 hours."

        elif score >= 70:
            approach = "QUALIFIED - Multi-touch sequence"
            approach += ". Start with educational content, then offer consultation. 3-5 day sequence."

        else:
            approach = "NURTURE - Low-key engagement"
            approach += ". Share case studies and thought leadership. Monthly check-ins."

        # Custom value proposition
        value_prop = f"LeniLani helps {industry} businesses in Hawaii "

        if pain_points:
            value_prop += f"solve {pain_points[0]} "

        value_prop += "through AI-powered automation and machine learning solutions. "
        value_prop += "Local expertise, proven results, rapid implementation."

        return {
            'talking_points': talking_points,
            'recommended_approach': approach,
            'value_proposition': value_prop
        }

    async def save_enrichment_to_db(self, enrichment: Dict) -> bool:
        """
        Save enrichment data to database (attaches to lead record)

        Updates the lead with:
        - decision_makers (JSON array)
        - research_summary (text)
        - talking_points (JSON array)
        - recommended_approach (text)
        - enrichment_status (completed/failed)
        """
        lead_id = enrichment.get('lead_id')

        if not lead_id:
            print(f"  ❌ No lead_id in enrichment data")
            return False

        try:
            # Prepare update data
            update_data = {
                'decision_makers': enrichment.get('decision_makers', []),
                'research_summary': enrichment.get('research_summary'),
                'pain_points': enrichment.get('pain_points', []),
                'talking_points': enrichment.get('talking_points', []),
                'recommended_approach': enrichment.get('recommended_approach'),
                'value_proposition': enrichment.get('value_proposition'),
                'enrichment_status': enrichment.get('enrichment_status', 'completed'),
                'enriched_at': enrichment.get('enriched_at'),
                'status': 'RESEARCHED'  # Update lead status
            }

            # Update lead in database
            result = await supabase_db.update_lead(lead_id, update_data)

            if result:
                print(f"  ✅ Enrichment saved for {enrichment.get('company_name')}")
                return True
            else:
                print(f"  ⚠️  Failed to save enrichment for {enrichment.get('company_name')}")
                return False

        except Exception as e:
            print(f"  ❌ Error saving enrichment: {e}")
            return False


class AutoEnrichmentOrchestrator:
    """
    Orchestrates automatic enrichment of newly discovered leads

    Runs after daily discovery to enrich all NEW leads before
    they're pushed to HubSpot
    """

    def __init__(self):
        self.pipeline = LeadEnrichmentPipeline()

    async def enrich_new_leads(
        self,
        status_filter: str = 'NEW',
        max_leads: int = 50
    ) -> Dict:
        """
        Find and enrich all leads with status='NEW'

        Args:
            status_filter: Lead status to filter (default: NEW)
            max_leads: Maximum number of leads to enrich in one run

        Returns:
            {
                'total_processed': 10,
                'successful': 8,
                'failed': 2,
                'enrichments': [...]
            }
        """
        print(f"\n🚀 Starting auto-enrichment for {status_filter} leads...")

        # Get leads needing enrichment
        leads = await supabase_db.get_leads(status=status_filter, limit=max_leads)

        if not leads:
            print(f"  ℹ️  No {status_filter} leads found")
            return {
                'total_processed': 0,
                'successful': 0,
                'failed': 0,
                'enrichments': []
            }

        print(f"  📋 Found {len(leads)} leads to enrich")

        # Enrich batch (with concurrency limit for rate limiting)
        enrichments = await self.pipeline.enrich_batch(leads, max_concurrent=3)

        # Save enrichments to database
        print(f"\n💾 Saving enrichments to database...")
        successful = 0
        failed = 0

        for enrichment in enrichments:
            if enrichment.get('enrichment_status') == 'completed':
                saved = await self.pipeline.save_enrichment_to_db(enrichment)
                if saved:
                    successful += 1
                else:
                    failed += 1
            else:
                failed += 1

        print(f"\n✅ Enrichment complete:")
        print(f"   Total Processed: {len(enrichments)}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")

        return {
            'total_processed': len(enrichments),
            'successful': successful,
            'failed': failed,
            'enrichments': enrichments
        }


# Singleton instances
_enrichment_pipeline = None
_auto_orchestrator = None


def get_enrichment_pipeline() -> LeadEnrichmentPipeline:
    """Get global enrichment pipeline instance"""
    global _enrichment_pipeline
    if _enrichment_pipeline is None:
        _enrichment_pipeline = LeadEnrichmentPipeline()
    return _enrichment_pipeline


def get_auto_orchestrator() -> AutoEnrichmentOrchestrator:
    """Get global auto-enrichment orchestrator"""
    global _auto_orchestrator
    if _auto_orchestrator is None:
        _auto_orchestrator = AutoEnrichmentOrchestrator()
    return _auto_orchestrator
