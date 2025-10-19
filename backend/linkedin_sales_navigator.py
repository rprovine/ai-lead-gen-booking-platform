"""
LinkedIn Sales Navigator Integration
Leverages Sales Navigator API for finding decision makers with verified contact info
"""

import os
import aiohttp
from typing import List, Dict, Optional
import json


class LinkedInSalesNavigator:
    """
    LinkedIn Sales Navigator integration for B2B lead generation

    Features:
    - Find decision makers at target companies
    - Get verified email addresses and phone numbers
    - Access TeamLink and InMail capabilities
    - Search by seniority level, function, and geography
    - Get real-time job changes and company updates
    """

    def __init__(self):
        # LinkedIn Sales Navigator API credentials
        self.api_key = os.getenv('LINKEDIN_SALES_NAV_API_KEY')
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.base_url = "https://api.linkedin.com/v2"

    async def find_decision_makers_at_company(
        self,
        company_name: str,
        linkedin_company_id: Optional[str] = None,
        seniority_levels: List[str] = None,
        job_functions: List[str] = None,
        geography: str = "Hawaii",
        limit: int = 10
    ) -> List[Dict]:
        """
        Find decision makers at a specific company using Sales Navigator

        Args:
            company_name: Company name
            linkedin_company_id: LinkedIn company ID (if known)
            seniority_levels: ['C-Suite', 'VP', 'Director', 'Manager']
            job_functions: ['Information Technology', 'Operations', 'Marketing', 'Sales']
            geography: Geographic filter (e.g., 'Hawaii', 'Honolulu')
            limit: Max number of decision makers to return

        Returns:
            List of decision makers with contact info
        """
        if not self.api_key:
            print("⚠️  LinkedIn Sales Navigator API key not configured")
            return []

        # Default seniority levels for decision makers
        if not seniority_levels:
            seniority_levels = ['C-Suite', 'VP', 'Director']

        try:
            # First, get the LinkedIn company ID if not provided
            if not linkedin_company_id:
                linkedin_company_id = await self._search_company(company_name)

            if not linkedin_company_id:
                print(f"❌ Could not find LinkedIn company ID for {company_name}")
                return []

            # Search for people at this company
            decision_makers = await self._search_people_at_company(
                linkedin_company_id,
                seniority_levels,
                job_functions,
                geography,
                limit
            )

            # Enrich with contact information
            enriched = []
            for person in decision_makers:
                person_id = person.get('id')
                contact_info = await self._get_contact_info(person_id)

                enriched.append({
                    'linkedin_id': person_id,
                    'name': f"{person.get('firstName', '')} {person.get('lastName', '')}".strip(),
                    'title': person.get('headline', ''),
                    'current_position': person.get('currentPosition', {}).get('title'),
                    'email': contact_info.get('email'),
                    'phone': contact_info.get('phone'),
                    'linkedin_url': f"https://www.linkedin.com/in/{person.get('publicIdentifier', '')}",
                    'profile_picture': person.get('profilePicture'),
                    'location': person.get('location', {}).get('name'),
                    'seniority_level': person.get('seniorityLevel'),
                    'years_in_position': person.get('currentPosition', {}).get('duration'),
                    'company_tenure': person.get('tenure'),
                    'shared_connections': person.get('sharedConnections', {}).get('total', 0),
                    'teamlink_access': contact_info.get('teamlink_access', False),
                    'inmail_available': contact_info.get('inmail_available', True),
                    'confidence': 'high',  # Sales Navigator data is verified
                    'source': 'linkedin_sales_navigator'
                })

            print(f"✓ LinkedIn Sales Navigator: Found {len(enriched)} decision makers at {company_name}")
            return enriched

        except Exception as e:
            print(f"LinkedIn Sales Navigator error: {e}")
            return []

    async def _search_company(self, company_name: str) -> Optional[str]:
        """
        Search for company and get LinkedIn company ID
        """
        try:
            url = f"{self.base_url}/organizationSearch"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            params = {
                'q': 'keywords',
                'keywords': company_name,
                'count': 1
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('elements'):
                            return str(data['elements'][0].get('id'))

        except Exception as e:
            print(f"Company search error: {e}")

        return None

    async def _search_people_at_company(
        self,
        company_id: str,
        seniority_levels: List[str],
        job_functions: List[str],
        geography: str,
        limit: int
    ) -> List[Dict]:
        """
        Search for people at a company with filters
        """
        try:
            # Sales Navigator People Search API
            url = f"{self.base_url}/peopleSearch"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'X-Restli-Protocol-Version': '2.0.0'
            }

            # Build search filters
            filters = {
                'currentCompany': [company_id]
            }

            if seniority_levels:
                filters['seniorityLevel'] = seniority_levels

            if job_functions:
                filters['function'] = job_functions

            if geography:
                filters['geoUrn'] = await self._get_geo_urn(geography)

            params = {
                'q': 'search',
                'filters': json.dumps(filters),
                'count': limit,
                'start': 0
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('elements', [])

        except Exception as e:
            print(f"People search error: {e}")

        return []

    async def _get_contact_info(self, person_id: str) -> Dict:
        """
        Get contact information for a person (Sales Navigator premium feature)
        """
        try:
            # Sales Navigator Contact Info API
            url = f"{self.base_url}/salesPersonContactInfo/{person_id}"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'X-Restli-Protocol-Version': '2.0.0'
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'email': data.get('emailAddress'),
                            'phone': data.get('phoneNumber'),
                            'teamlink_access': data.get('teamLinkAccess', False),
                            'inmail_available': data.get('inmailAvailable', True)
                        }

        except Exception as e:
            print(f"Contact info error: {e}")

        return {}

    async def _get_geo_urn(self, geography: str) -> Optional[str]:
        """
        Convert geography name to LinkedIn URN
        """
        # Hardcoded URNs for Hawaii locations (these can be fetched via API)
        geo_mapping = {
            'hawaii': 'urn:li:fs_geo:103607527',  # Hawaii state
            'honolulu': 'urn:li:fs_geo:106006644',  # Honolulu
            'maui': 'urn:li:fs_geo:105609091',  # Maui
            'kauai': 'urn:li:fs_geo:106033894',  # Kauai
            'big island': 'urn:li:fs_geo:105839952',  # Big Island
            'hilo': 'urn:li:fs_geo:104712053',  # Hilo
            'kona': 'urn:li:fs_geo:104926564',  # Kona
        }

        return geo_mapping.get(geography.lower())

    async def track_job_changes(self, person_ids: List[str]) -> List[Dict]:
        """
        Track job changes for a list of people (Sales Navigator feature)
        Useful for knowing when decision makers change roles
        """
        try:
            url = f"{self.base_url}/salesJobChanges"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            params = {
                'ids': ','.join(person_ids)
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('elements', [])

        except Exception as e:
            print(f"Job changes tracking error: {e}")

        return []


# Example usage
async def main():
    """Test LinkedIn Sales Navigator integration"""
    nav = LinkedInSalesNavigator()

    decision_makers = await nav.find_decision_makers_at_company(
        company_name="Hawaiian Airlines",
        seniority_levels=['C-Suite', 'VP'],
        job_functions=['Information Technology', 'Operations'],
        geography="Honolulu",
        limit=5
    )

    print("\n" + "="*60)
    print("DECISION MAKERS FROM LINKEDIN SALES NAVIGATOR")
    print("="*60)

    for person in decision_makers:
        print(f"\n{person['name']} - {person['title']}")
        if person.get('email'):
            print(f"  ✉️  {person['email']}")
        if person.get('phone'):
            print(f"  📞 {person['phone']}")
        print(f"  🔗 {person['linkedin_url']}")
        print(f"  📍 {person['location']}")
        print(f"  👥 {person['shared_connections']} shared connections")
        if person.get('teamlink_access'):
            print(f"  ✅ TeamLink access available")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
