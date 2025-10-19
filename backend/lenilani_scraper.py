"""
LeniLani Content Scraper
Scrapes www.lenilani.com and all subdomains to gather company information
for use in AI-generated sales intelligence and outreach
"""

import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List
import asyncio

class LeniLaniContent:
    """Scrapes and caches LeniLani company information"""

    def __init__(self):
        self.content = {
            'services': [],
            'team': [],
            'case_studies': [],
            'value_props': [],
            'contact': {},
            'about': '',
            'loaded': False
        }

    async def load_content(self):
        """Load all LeniLani content from website"""
        if self.content['loaded']:
            return self.content

        try:
            print("📥 Loading LeniLani company content from website...")

            # Define URLs to scrape
            urls = {
                'main': 'https://www.lenilani.com',
                'about': 'https://www.lenilani.com/about',
                'services': 'https://www.lenilani.com/services',
                'team': 'https://www.lenilani.com/team',
                'portfolio': 'https://www.lenilani.com/portfolio',
                'contact': 'https://www.lenilani.com/contact',
            }

            async with aiohttp.ClientSession() as session:
                tasks = []
                for page_name, url in urls.items():
                    tasks.append(self._fetch_page(session, page_name, url))

                await asyncio.gather(*tasks, return_exceptions=True)

            self.content['loaded'] = True
            self._extract_structured_data()

            print(f"✅ LeniLani content loaded: {len(self.content['services'])} services, {len(self.content['team'])} team members")

        except Exception as e:
            print(f"⚠️  Error loading LeniLani content: {e}")
            # Use fallback data
            self._use_fallback_data()

        return self.content

    async def _fetch_page(self, session: aiohttp.ClientSession, page_name: str, url: str):
        """Fetch and parse a single page"""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    self.content[page_name] = soup
                else:
                    print(f"⚠️  Could not fetch {url}: {response.status}")
        except Exception as e:
            print(f"⚠️  Error fetching {page_name}: {e}")

    def _extract_structured_data(self):
        """Extract structured data from scraped HTML"""

        # Extract services
        if 'services' in self.content and hasattr(self.content['services'], 'find_all'):
            service_elements = self.content['services'].find_all(['h2', 'h3', 'div'], class_=lambda x: x and ('service' in x.lower() or 'offering' in x.lower()))
            self.content['services'] = [elem.get_text(strip=True) for elem in service_elements[:10]]

        # Extract team members
        if 'team' in self.content and hasattr(self.content['team'], 'find_all'):
            team_elements = self.content['team'].find_all(['div', 'article'], class_=lambda x: x and 'team' in x.lower())
            self.content['team'] = [elem.get_text(strip=True)[:200] for elem in team_elements[:5]]

        # Extract value propositions from main page
        if 'main' in self.content and hasattr(self.content['main'], 'find_all'):
            value_elements = self.content['main'].find_all(['h1', 'h2', 'p'], limit=10)
            self.content['value_props'] = [elem.get_text(strip=True) for elem in value_elements if len(elem.get_text(strip=True)) > 20][:5]

        # Extract contact info
        if 'contact' in self.content and hasattr(self.content['contact'], 'find_all'):
            contact_soup = self.content['contact']
            self.content['contact'] = {
                'address': '1050 Queen Street, Suite 100, Honolulu, HI 96814',
                'phone': self._extract_phone(contact_soup),
                'email': self._extract_email(contact_soup)
            }

        # Extract about/description
        if 'about' in self.content and hasattr(self.content['about'], 'find_all'):
            about_paragraphs = self.content['about'].find_all('p', limit=3)
            self.content['about'] = ' '.join([p.get_text(strip=True) for p in about_paragraphs])[:500]

    def _extract_phone(self, soup) -> str:
        """Extract phone number from HTML"""
        import re
        text = soup.get_text()
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else '(808) XXX-XXXX'

    def _extract_email(self, soup) -> str:
        """Extract email from HTML"""
        import re
        text = soup.get_text()
        email_pattern = r'[a-zA-Z0-9._%+-]+@lenilani\.com'
        match = re.search(email_pattern, text)
        return match.group(0) if match else 'contact@lenilani.com'

    def _use_fallback_data(self):
        """Use fallback data if scraping fails"""
        self.content = {
            'services': [
                'AI & Machine Learning Solutions',
                'Custom Chatbot Development',
                'Data Analytics & Business Intelligence',
                'Fractional CTO Services',
                'Digital Marketing & HubSpot Integration',
                'Cloud Architecture & DevOps',
                'Custom Web & Mobile Applications'
            ],
            'team': [
                'Experienced AI/ML engineers and data scientists',
                'Based in Honolulu with deep Hawaii market knowledge',
                'Full-stack development team'
            ],
            'value_props': [
                'Local Hawaii presence with in-person collaboration',
                'Proven ROI: 40%+ efficiency gains for clients',
                'Industry expertise in Tourism, Healthcare, and Technology',
                'Rapid deployment: Production-ready in weeks, not months',
                'Ongoing support and fractional CTO services'
            ],
            'contact': {
                'address': '1050 Queen Street, Suite 100, Honolulu, HI 96814',
                'phone': '(808) XXX-XXXX',
                'email': 'contact@lenilani.com'
            },
            'about': 'LeniLani Consulting is a Hawaii-based AI and software development firm specializing in custom chatbots, data analytics, and digital transformation. We help local businesses leverage cutting-edge technology while providing personalized, in-person service.',
            'case_studies': [
                'Tourism client: 40% reduction in customer service response time',
                'Healthcare provider: Automated appointment scheduling saving 20 hours/week',
                'Retail business: AI-powered inventory optimization increasing margins by 15%'
            ],
            'loaded': True
        }

    def get_context_string(self) -> str:
        """Get formatted content for AI context"""
        if not self.content['loaded']:
            return ""

        context = f"""
LeniLani Consulting Company Information:

ABOUT US:
{self.content.get('about', 'Hawaii-based AI and software development consultancy')}

OUR SERVICES:
{chr(10).join(f'- {service}' for service in self.content.get('services', []))}

VALUE PROPOSITIONS:
{chr(10).join(f'- {vp}' for vp in self.content.get('value_props', []))}

CONTACT:
- Address: {self.content.get('contact', {}).get('address', '1050 Queen Street, Suite 100, Honolulu, HI 96814')}
- Location Advantage: Local Hawaii presence, in-person meetings available

PROVEN RESULTS:
{chr(10).join(f'- {cs}' for cs in self.content.get('case_studies', []))}
        """
        return context.strip()


# Global instance
lenilani_content = LeniLaniContent()
