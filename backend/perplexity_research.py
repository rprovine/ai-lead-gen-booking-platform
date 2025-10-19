"""
Perplexity AI Research Service
Gathers recent news, leadership updates, and business intelligence about companies
"""

import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from openai import OpenAI


class PerplexityResearcher:
    """
    Uses Perplexity AI to research companies and gather recent intelligence
    Focuses on news from the past 90 days
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Perplexity client"""
        self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')

        if not self.api_key:
            print("⚠️  Perplexity API key not found - research features disabled")
            self.client = None
        else:
            # Perplexity uses OpenAI-compatible API
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.perplexity.ai"
            )
            print("✅ Perplexity AI research enabled")

    async def research_company(
        self,
        company_name: str,
        industry: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict:
        """
        Conduct comprehensive research on a company

        Args:
            company_name: Name of the company
            industry: Industry/sector (helps narrow search)
            location: Location (e.g., "Hawaii", "Honolulu")

        Returns:
            Dictionary with research findings
        """
        if not self.client:
            return self._empty_research()

        try:
            # Calculate 90 days ago for recency filter
            ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime("%B %Y")

            # Build location context
            location_str = f" in {location}" if location else ""
            industry_str = f" ({industry})" if industry else ""

            # Comprehensive research query
            query = f"""Research {company_name}{industry_str}{location_str}.

Focus on information from the past 90 days (since {ninety_days_ago}):

1. **Recent News & Announcements**: Any major news, press releases, or announcements
2. **Leadership Updates**: New hires, promotions, executive changes, key management
3. **Business Developments**: Expansion plans, new products/services, partnerships, funding
4. **Market Position**: Industry trends affecting them, competitive landscape
5. **Challenges & Opportunities**: Pain points they might be facing, growth opportunities

Provide specific, factual information with dates when available. If no recent information is found, say so clearly."""

            # Call Perplexity API
            response = self.client.chat.completions.create(
                model="sonar-pro",  # Perplexity Sonar Pro - best for deep research (2025)
                messages=[
                    {
                        "role": "system",
                        "content": "You are a business research analyst. Provide factual, recent information about companies with specific dates and sources when possible."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                temperature=0.2,  # Low temperature for factual responses
                max_tokens=3000  # Increased for more detailed research
            )

            research_text = response.choices[0].message.content

            # Parse the research into structured format
            return self._parse_research(research_text, company_name)

        except Exception as e:
            print(f"Error researching {company_name}: {e}")
            return self._empty_research()

    async def quick_news_search(self, company_name: str, location: Optional[str] = None) -> str:
        """
        Quick search for most recent news about a company

        Args:
            company_name: Company name
            location: Location filter

        Returns:
            Brief summary of recent news
        """
        if not self.client:
            return "No recent news available"

        try:
            location_str = f" in {location}" if location else ""

            response = self.client.chat.completions.create(
                model="sonar-pro",  # Perplexity Sonar Pro - best for deep research (2025)
                messages=[
                    {
                        "role": "system",
                        "content": "Provide a brief 2-3 sentence summary of the most recent news about this company."
                    },
                    {
                        "role": "user",
                        "content": f"What's the most recent news about {company_name}{location_str} in the past 90 days?"
                    }
                ],
                temperature=0.2,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error in quick news search: {e}")
            return "Unable to fetch recent news"

    def _parse_research(self, research_text: str, company_name: str) -> Dict:
        """
        Parse Perplexity research response into structured format

        Args:
            research_text: Raw research text from Perplexity
            company_name: Company name

        Returns:
            Structured research data
        """
        # Extract key sections from the research
        sections = {
            "recent_news": self._extract_section(research_text, ["recent news", "announcements"]),
            "leadership": self._extract_section(research_text, ["leadership", "executive", "management"]),
            "business_developments": self._extract_section(research_text, ["business developments", "expansion", "partnerships", "funding"]),
            "market_position": self._extract_section(research_text, ["market position", "trends", "competitive"]),
            "challenges_opportunities": self._extract_section(research_text, ["challenges", "opportunities", "pain points"])
        }

        # Determine if substantial research was found
        has_data = any(len(section) > 50 for section in sections.values())

        return {
            "company_name": company_name,
            "research_date": datetime.now().isoformat(),
            "has_recent_data": has_data,
            "full_text": research_text,
            **sections,
            "summary": self._generate_summary(research_text, has_data)
        }

    def _extract_section(self, text: str, keywords: List[str]) -> str:
        """Extract a specific section from research text based on keywords"""
        text_lower = text.lower()

        for keyword in keywords:
            if keyword in text_lower:
                # Find the section
                start_idx = text_lower.find(keyword)
                # Find next section or end
                next_section_idx = text.find("\n\n", start_idx + len(keyword))

                if next_section_idx == -1:
                    section = text[start_idx:]
                else:
                    section = text[start_idx:next_section_idx]

                return section.strip()

        return ""

    def _generate_summary(self, research_text: str, has_data: bool) -> str:
        """Generate a brief summary of the research"""
        if not has_data or "no recent information" in research_text.lower():
            return "No significant recent news or developments found in the past 90 days."

        # Get first few sentences as summary
        sentences = research_text.split('. ')[:3]
        return '. '.join(sentences) + '.'

    def _empty_research(self) -> Dict:
        """Return empty research structure"""
        return {
            "company_name": "",
            "research_date": datetime.now().isoformat(),
            "has_recent_data": False,
            "full_text": "Research unavailable",
            "recent_news": "",
            "leadership": "",
            "business_developments": "",
            "market_position": "",
            "challenges_opportunities": "",
            "summary": "Perplexity research not available"
        }


# Example usage
async def main():
    """Example usage of Perplexity researcher"""
    researcher = PerplexityResearcher()

    # Research a Hawaii company
    research = await researcher.research_company(
        company_name="Hawaiian Airlines",
        industry="Aviation",
        location="Hawaii"
    )

    print(f"\n{'='*60}")
    print(f"Research for: {research['company_name']}")
    print(f"{'='*60}\n")
    print(f"Summary: {research['summary']}\n")

    if research['recent_news']:
        print(f"Recent News:\n{research['recent_news']}\n")

    if research['leadership']:
        print(f"Leadership Updates:\n{research['leadership']}\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
