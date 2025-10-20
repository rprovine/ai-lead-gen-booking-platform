"""
Executive & Decision Maker Contact Finder
Finds key decision makers and their contact information for B2B sales
"""

import os
import re
import aiohttp
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import json


class ExecutiveContactFinder:
    """
    Finds decision maker contact information using multiple sources:
    - Hunter.io for email addresses
    - Apollo.io for executive contacts
    - RocketReach for phone numbers
    - LinkedIn for profiles
    - Website scraping for team pages
    """

    def __init__(self):
        self.hunter_api_key = os.getenv('HUNTER_API_KEY')
        self.apollo_api_key = os.getenv('APOLLO_API_KEY')
        self.rocketreach_api_key = os.getenv('ROCKETREACH_API_KEY')
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_cse_id = os.getenv('GOOGLE_CSE_ID')

    async def find_decision_makers(
        self,
        company_name: str,
        website: str,
        industry: str = None,
        employee_count: int = None
    ) -> Dict:
        """
        Find decision makers and their contact information

        Returns:
            {
                "executives": [
                    {
                        "name": "John Smith",
                        "title": "CEO",
                        "email": "john.smith@company.com",
                        "phone": "+1-808-555-1234",
                        "linkedin": "https://linkedin.com/in/johnsmith",
                        "confidence": "high"  # high, medium, low
                    }
                ],
                "email_pattern": "firstname.lastname@company.com",
                "company_domain": "company.com"
            }
        """
        result = {
            "executives": [],
            "email_pattern": None,
            "company_domain": self._extract_domain(website)
        }

        # 1. Try Hunter.io for email pattern and executive emails
        if self.hunter_api_key:
            hunter_data = await self._search_hunter(company_name, result['company_domain'])
            if hunter_data:
                result['email_pattern'] = hunter_data.get('pattern')
                result['executives'].extend(hunter_data.get('emails', []))

        # 2. Try Apollo.io for executive contacts (best for B2B)
        if self.apollo_api_key:
            apollo_data = await self._search_apollo(company_name, result['company_domain'])
            if apollo_data:
                result['executives'].extend(apollo_data)

        # 3. Try RocketReach for phone numbers and additional contacts
        if self.rocketreach_api_key:
            rocketreach_data = await self._search_rocketreach(company_name)
            if rocketreach_data:
                result['executives'].extend(rocketreach_data)

        # 4. Use Perplexity AI to find decision makers (especially good for small businesses)
        if self.perplexity_api_key and len(result['executives']) < 3:
            perplexity_data = await self._search_perplexity_contacts(company_name, website)
            if perplexity_data:
                result['executives'].extend(perplexity_data)

        # 5. Use Google Search to find owner/CEO information
        if self.google_api_key and len(result['executives']) < 3:
            google_data = await self._search_google_contacts(company_name, website)
            if google_data:
                result['executives'].extend(google_data)

        # 6. Scrape company website for team/about pages
        if website:
            website_executives = await self._scrape_team_page(website)
            result['executives'].extend(website_executives)

        # 7. Generate email guesses using common patterns
        if result['company_domain'] and result['executives']:
            result['executives'] = self._enhance_with_email_guesses(
                result['executives'],
                result['company_domain'],
                result.get('email_pattern')
            )

        # Deduplicate executives by email/name
        result['executives'] = self._deduplicate_executives(result['executives'])

        # Prioritize by decision-making power
        result['executives'] = self._prioritize_by_title(result['executives'])

        return result

    async def _search_hunter(self, company_name: str, domain: str) -> Optional[Dict]:
        """
        Search Hunter.io for email addresses and patterns
        API: https://hunter.io/api-documentation/v2
        """
        print(f"🔍 Hunter.io: Searching for {domain}...")
        print(f"   API key configured: {bool(self.hunter_api_key)}")
        print(f"   Domain: {domain}")

        if not self.hunter_api_key or not domain:
            print(f"   ⚠️  Skipping - missing API key or domain")
            return None

        try:
            url = "https://api.hunter.io/v2/domain-search"
            params = {
                'domain': domain,
                'api_key': self.hunter_api_key,
                'limit': 10
            }

            print(f"   Making request to: {url}")
            print(f"   Params: domain={domain}, limit=10")

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    print(f"   Response status: {response.status}")

                    if response.status == 200:
                        data = await response.json()
                        print(f"   Response data keys: {list(data.keys())}")

                        # Log the actual data structure
                        if 'data' in data:
                            print(f"   Total emails found: {len(data.get('data', {}).get('emails', []))}")
                            print(f"   Email pattern: {data.get('data', {}).get('pattern')}")

                        result = {
                            'pattern': data.get('data', {}).get('pattern'),
                            'emails': []
                        }

                        # Extract executive emails
                        for email_data in data.get('data', {}).get('emails', []):
                            # Filter for decision makers
                            # Handle None values from position field
                            title = (email_data.get('position') or '').lower()
                            if self._is_decision_maker_title(title):
                                result['emails'].append({
                                    'name': f"{email_data.get('first_name', '')} {email_data.get('last_name', '')}".strip(),
                                    'title': email_data.get('position') or '',
                                    'email': email_data.get('value'),
                                    'linkedin': email_data.get('linkedin'),
                                    'confidence': email_data.get('confidence', 0) / 100,  # Convert to 0-1
                                    'source': 'hunter.io'
                                })

                        print(f"✓ Hunter.io: Found {len(result['emails'])} executives for {domain}")
                        return result
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Hunter.io API error: {response.status}")
                        print(f"   Error response: {error_text[:500]}")

        except Exception as e:
            print(f"❌ Hunter.io error: {e}")
            import traceback
            print(traceback.format_exc())

        return None

    async def _search_apollo(self, company_name: str, domain: str) -> List[Dict]:
        """
        Search Apollo.io for executive contacts
        API: https://www.apollo.io/api
        """
        print(f"🔍 Apollo.io: Searching for {company_name} ({domain})...")
        print(f"   API key configured: {bool(self.apollo_api_key)}")

        if not self.apollo_api_key:
            print(f"   ⚠️  Skipping - missing API key")
            return []

        try:
            # Use /contacts/search endpoint (available on Basic plan)
            url = "https://api.apollo.io/v1/contacts/search"
            headers = {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache',
                'X-Api-Key': self.apollo_api_key
            }

            payload = {
                "q_organization_domains": domain,
                "page": 1,
                "per_page": 10,
                "person_titles": [
                    "CEO", "Chief Executive Officer",
                    "CTO", "Chief Technology Officer",
                    "COO", "Chief Operating Officer",
                    "President", "Owner", "Founder",
                    "VP", "Vice President",
                    "Director"
                ]
            }

            print(f"   Making request to: {url}")
            print(f"   Payload: domain={domain}, per_page=10")

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    print(f"   Response status: {response.status}")

                    if response.status == 200:
                        data = await response.json()
                        print(f"   Response data keys: {list(data.keys())}")

                        # /contacts/search returns 'contacts' instead of 'people'
                        contacts = data.get('contacts', [])
                        print(f"   Total contacts found: {len(contacts)}")

                        executives = []
                        for person in contacts:
                            exec_data = {
                                'name': person.get('name'),
                                'title': person.get('title'),
                                'email': person.get('email'),
                                'phone': person.get('phone_numbers', [{}])[0].get('sanitized_number') if person.get('phone_numbers') else None,
                                'linkedin': person.get('linkedin_url'),
                                'confidence': 'high',
                                'source': 'apollo.io'
                            }
                            executives.append(exec_data)
                            print(f"   Found: {exec_data['name']} - {exec_data['title']}")

                        print(f"✓ Apollo.io: Found {len(executives)} executives for {company_name}")
                        return executives
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Apollo.io API error: {response.status}")
                        print(f"   Error response: {error_text[:500]}")

        except Exception as e:
            print(f"❌ Apollo.io error: {e}")
            import traceback
            print(traceback.format_exc())

        return []

    async def _search_rocketreach(self, company_name: str) -> List[Dict]:
        """
        Search RocketReach for executive phone numbers
        API: https://rocketreach.co/api
        """
        if not self.rocketreach_api_key:
            return []

        try:
            url = "https://api.rocketreach.co/v2/api/search"
            headers = {
                'Api-Key': self.rocketreach_api_key
            }

            params = {
                'current_employer': company_name,
                'start': 0,
                'page_size': 10
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        executives = []
                        for profile in data.get('profiles', []):
                            # Only include decision makers
                            title = profile.get('current_title', '').lower()
                            if self._is_decision_maker_title(title):
                                executives.append({
                                    'name': profile.get('name'),
                                    'title': profile.get('current_title'),
                                    'email': profile.get('emails', [{}])[0].get('email') if profile.get('emails') else None,
                                    'phone': profile.get('phones', [{}])[0].get('number') if profile.get('phones') else None,
                                    'linkedin': profile.get('linkedin_url'),
                                    'confidence': 'medium',
                                    'source': 'rocketreach'
                                })

                        print(f"✓ RocketReach: Found {len(executives)} executives for {company_name}")
                        return executives

        except Exception as e:
            print(f"RocketReach error: {e}")

        return []

    async def _search_perplexity_contacts(self, company_name: str, website: str) -> List[Dict]:
        """
        Use Perplexity AI to find decision makers and contact information
        Especially effective for small businesses not in traditional databases
        """
        if not self.perplexity_api_key:
            return []

        print(f"🔍 Perplexity AI: Searching for decision makers at {company_name}...")

        try:
            # Craft a specific prompt to find owner/CEO contact info
            prompt = f"""Find the owner, CEO, or key decision makers for {company_name} (website: {website}).

Please provide:
1. Full name of the owner/CEO/president
2. Their job title
3. Email address (if publicly available)
4. Phone number (if publicly available)
5. LinkedIn profile URL (if available)

Focus on publicly available contact information from:
- Company website
- LinkedIn
- Business directories
- Press releases
- News articles
- Professional profiles

Format your response as a JSON array of decision makers:
[
  {{
    "name": "Full Name",
    "title": "CEO/Owner/President",
    "email": "email@company.com",
    "phone": "+1-808-555-1234",
    "linkedin": "https://linkedin.com/in/profile"
  }}
]

Only include real, verified information. If you can't find a piece of information, omit that field."""

            url = "https://api.perplexity.ai/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "sonar-pro",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a business research assistant. Provide accurate, publicly available contact information in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 1000
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Extract the response text
                        response_text = data.get('choices', [{}])[0].get('message', {}).get('content', '')

                        # Try to parse JSON from the response
                        try:
                            # Look for JSON array in the response
                            import re
                            json_match = re.search(r'\[[\s\S]*?\]', response_text)
                            if json_match:
                                contacts = json.loads(json_match.group())

                                # Convert to our format
                                executives = []
                                for contact in contacts:
                                    if contact.get('name'):
                                        exec_data = {
                                            'name': contact.get('name'),
                                            'title': contact.get('title', 'Owner'),
                                            'email': contact.get('email'),
                                            'phone': contact.get('phone'),
                                            'linkedin': contact.get('linkedin'),
                                            'confidence': 0.7,  # Medium-high confidence from Perplexity
                                            'source': 'perplexity.ai'
                                        }
                                        executives.append(exec_data)
                                        print(f"   Found: {exec_data['name']} - {exec_data['title']}")

                                print(f"✓ Perplexity AI: Found {len(executives)} decision makers for {company_name}")
                                return executives
                        except json.JSONDecodeError:
                            print(f"   ⚠️  Could not parse JSON from Perplexity response")
                            print(f"   Raw response: {response_text[:200]}...")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Perplexity API error: {response.status}")
                        print(f"   Error response: {error_text[:500]}")

        except Exception as e:
            print(f"❌ Perplexity error: {e}")

        return []

    async def _search_google_contacts(self, company_name: str, website: str) -> List[Dict]:
        """
        Use Google Custom Search to find owner/CEO information
        """
        if not self.google_api_key or not self.google_cse_id:
            return []

        print(f"🔍 Google Search: Searching for decision makers at {company_name}...")

        try:
            # Search for owner/CEO information
            search_queries = [
                f"{company_name} owner contact",
                f"{company_name} CEO email",
                f"{company_name} president Hawaii"
            ]

            executives = []

            for query in search_queries:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': self.google_api_key,
                    'cx': self.google_cse_id,
                    'q': query,
                    'num': 3
                }

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()

                            # Analyze search results for contact information
                            for item in data.get('items', []):
                                snippet = item.get('snippet', '')
                                title = item.get('title', '')

                                # Extract emails from snippets
                                emails = self._extract_emails_from_html(snippet + " " + title)

                                for email in emails:
                                    if not any(skip in email.lower() for skip in ['info@', 'support@', 'contact@']):
                                        # Try to extract name from context
                                        name_match = re.search(r'([A-Z][a-z]+\s[A-Z][a-z]+)[\s,]+(CEO|Owner|President|Founder)', snippet + " " + title)
                                        name = name_match.group(1) if name_match else None
                                        title_match = name_match.group(2) if name_match else 'Owner'

                                        executives.append({
                                            'name': name,
                                            'title': title_match,
                                            'email': email,
                                            'phone': None,
                                            'linkedin': None,
                                            'confidence': 0.5,  # Lower confidence from Google search
                                            'source': 'google_search'
                                        })

            if executives:
                print(f"✓ Google Search: Found {len(executives)} potential contacts for {company_name}")

            return executives[:3]  # Limit to top 3 results

        except Exception as e:
            print(f"❌ Google Search error: {e}")

        return []

    async def _scrape_team_page(self, website: str) -> List[Dict]:
        """
        Scrape company website for team/about/leadership/contact pages
        """
        executives = []

        try:
            # Common team and contact page URLs
            team_urls = [
                f"{website}/team",
                f"{website}/about",
                f"{website}/leadership",
                f"{website}/about-us",
                f"{website}/our-team",
                f"{website}/management",
                f"{website}/contact",
                f"{website}/contact-us"
            ]

            async with aiohttp.ClientSession() as session:
                for url in team_urls:
                    try:
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')

                                # Look for executive names and titles
                                team_members = self._extract_team_members(soup)

                                # Also extract all email addresses from the page using regex
                                emails_found = self._extract_emails_from_html(html)

                                if emails_found:
                                    print(f"✓ Website scrape: Found {len(emails_found)} email addresses at {url}")
                                    # Add generic contacts if we found emails but no structured team data
                                    if not team_members:
                                        for email in emails_found:
                                            # Filter out common non-decision maker emails
                                            if not any(skip in email.lower() for skip in ['info@', 'support@', 'hello@', 'contact@', 'sales@']):
                                                team_members.append({
                                                    'name': None,
                                                    'title': 'Contact',
                                                    'email': email,
                                                    'phone': None,
                                                    'linkedin': None,
                                                    'confidence': 'low',
                                                    'source': 'website'
                                                })

                                executives.extend(team_members)

                                if team_members:
                                    print(f"✓ Website scrape: Found {len(team_members)} team members at {url}")
                                    if 'contact' not in url:  # Keep searching contact pages even if we found team
                                        continue
                                    else:
                                        break  # Stop after finding contact page

                    except Exception as e:
                        continue

        except Exception as e:
            print(f"Website scraping error: {e}")

        return executives

    def _extract_emails_from_html(self, html: str) -> List[str]:
        """
        Extract all email addresses from HTML using regex
        """
        import re

        # Email regex pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, html)

        # Remove duplicates and common non-personal emails
        unique_emails = list(set(emails))

        # Filter out image files and other false positives
        filtered = [
            email for email in unique_emails
            if not any(ext in email.lower() for ext in ['.png', '.jpg', '.gif', '.svg', 'sentry', 'example.com'])
        ]

        return filtered[:10]  # Limit to first 10 unique emails

    def _extract_team_members(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract team member information from HTML
        """
        members = []

        # Look for common patterns
        patterns = [
            {'element': 'div', 'class': ['team-member', 'staff-member', 'leadership-member']},
            {'element': 'div', 'class': ['person', 'employee', 'executive']},
            {'element': 'article', 'class': ['team', 'staff', 'leadership']}
        ]

        for pattern in patterns:
            elements = soup.find_all(pattern['element'], class_=pattern.get('class'))

            for element in elements:
                name_elem = element.find(['h2', 'h3', 'h4', 'p'], class_=re.compile(r'name|title'))
                title_elem = element.find(['p', 'span', 'div'], class_=re.compile(r'position|title|role'))
                email_elem = element.find('a', href=re.compile(r'mailto:'))

                if name_elem:
                    name = name_elem.get_text(strip=True)
                    title = title_elem.get_text(strip=True) if title_elem else ''
                    email = email_elem['href'].replace('mailto:', '') if email_elem else None

                    # Only include if they're a decision maker
                    if self._is_decision_maker_title(title):
                        members.append({
                            'name': name,
                            'title': title,
                            'email': email,
                            'phone': None,
                            'linkedin': None,
                            'confidence': 'medium',
                            'source': 'website'
                        })

        return members

    def _enhance_with_email_guesses(
        self,
        executives: List[Dict],
        domain: str,
        pattern: Optional[str] = None
    ) -> List[Dict]:
        """
        Generate educated guesses for missing email addresses
        """
        for exec in executives:
            if not exec.get('email') and exec.get('name'):
                exec['email'] = self._guess_email(exec['name'], domain, pattern)
                exec['email_guessed'] = True

        return executives

    def _guess_email(self, name: str, domain: str, pattern: Optional[str] = None) -> Optional[str]:
        """
        Guess email address using common patterns

        Patterns:
        - firstname.lastname@domain.com (most common)
        - firstname@domain.com
        - firstnamelastname@domain.com
        - f.lastname@domain.com
        """
        if not name or not domain:
            return None

        parts = name.lower().strip().split()
        if len(parts) < 2:
            return f"{parts[0]}@{domain}"

        first_name = parts[0]
        last_name = parts[-1]

        # Use pattern if provided by Hunter.io
        if pattern:
            email = pattern.replace('{first}', first_name)
            email = email.replace('{last}', last_name)
            email = email.replace('{f}', first_name[0])
            email = email.replace('{l}', last_name[0])
            return email

        # Default: firstname.lastname (70% of companies use this)
        return f"{first_name}.{last_name}@{domain}"

    def _is_decision_maker_title(self, title: str) -> bool:
        """
        Check if title indicates a decision maker
        """
        if not title:
            return False

        title_lower = title.lower()

        decision_maker_keywords = [
            'ceo', 'chief executive',
            'cto', 'chief technology',
            'coo', 'chief operating',
            'cfo', 'chief financial',
            'president',
            'owner',
            'founder',
            'co-founder',
            'managing director',
            'executive director',
            'vp', 'vice president',
            'director',
            'head of',
            'general manager',
            'partner'
        ]

        return any(keyword in title_lower for keyword in decision_maker_keywords)

    def _prioritize_by_title(self, executives: List[Dict]) -> List[Dict]:
        """
        Sort executives by decision-making power
        """
        priority_order = {
            'ceo': 1, 'chief executive': 1, 'president': 1, 'owner': 1, 'founder': 1,
            'cto': 2, 'chief technology': 2,
            'coo': 3, 'chief operating': 3,
            'cfo': 4, 'chief financial': 4,
            'vp': 5, 'vice president': 5,
            'director': 6,
            'head': 7,
            'manager': 8
        }

        def get_priority(exec):
            title = exec.get('title', '').lower()
            for keyword, priority in priority_order.items():
                if keyword in title:
                    return priority
            return 99  # Low priority for unknown titles

        return sorted(executives, key=get_priority)

    def _deduplicate_executives(self, executives: List[Dict]) -> List[Dict]:
        """
        Remove duplicate executives based on email or name
        """
        seen = set()
        unique = []

        for exec in executives:
            # Use email as primary key, fall back to name
            key = exec.get('email') or exec.get('name', '').lower()

            if key and key not in seen:
                seen.add(key)
                unique.append(exec)
            elif key in seen:
                # Merge data from multiple sources
                existing = next((e for e in unique if (e.get('email') or e.get('name', '').lower()) == key), None)
                if existing:
                    # Fill in missing fields
                    for field in ['phone', 'linkedin', 'email', 'title']:
                        if not existing.get(field) and exec.get(field):
                            existing[field] = exec[field]

        return unique

    def _extract_domain(self, website: str) -> Optional[str]:
        """
        Extract domain from website URL
        """
        if not website:
            return None

        # Remove protocol
        domain = re.sub(r'^https?://', '', website)
        # Remove www
        domain = re.sub(r'^www\.', '', domain)
        # Remove path
        domain = domain.split('/')[0]

        return domain


# Example usage
async def main():
    """Test executive finder"""
    finder = ExecutiveContactFinder()

    result = await finder.find_decision_makers(
        company_name="Hawaiian Airlines",
        website="https://www.hawaiianairlines.com",
        industry="Aviation",
        employee_count=500
    )

    print("\n" + "="*60)
    print("DECISION MAKERS")
    print("="*60)
    print(f"\nEmail Pattern: {result['email_pattern']}")
    print(f"Company Domain: {result['company_domain']}\n")

    for exec in result['executives']:
        print(f"\n{exec['name']} - {exec['title']}")
        if exec.get('email'):
            print(f"  ✉️  {exec['email']}")
        if exec.get('phone'):
            print(f"  📞 {exec['phone']}")
        if exec.get('linkedin'):
            print(f"  🔗 {exec['linkedin']}")
        print(f"  Source: {exec['source']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
