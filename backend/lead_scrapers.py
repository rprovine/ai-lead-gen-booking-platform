"""
Real Lead Discovery Scrapers for Hawaii Businesses
Integrates multiple data sources: LinkedIn, Pacific Business News, Google, and more
"""

import asyncio
import aiohttp
import json
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse
from serpapi import GoogleSearch
import requests


class LinkedInScraper:
    """
    LinkedIn lead scraper using multiple approaches:
    1. LinkedIn Sales Navigator API (if credentials available)
    2. LinkedIn public company pages
    3. LinkedIn search results
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://www.linkedin.com"

    async def search_hawaii_companies(self, industry: str = None, size: str = None) -> List[Dict]:
        """
        Search for Hawaii-based companies on LinkedIn

        Args:
            industry: Target industry (e.g., 'tourism', 'healthcare')
            size: Company size ('1-10', '11-50', '51-200', '201-500', '501+')
        """
        leads = []

        # LinkedIn search queries for Hawaii businesses
        search_queries = [
            "hawaii tourism company",
            "hawaii hospitality business",
            "hawaii healthcare provider",
            "hawaii technology company",
            "honolulu business services",
            "hawaii consulting firm",
            "oahu retail business",
            "hawaii restaurant chain"
        ]

        if industry:
            search_queries = [f"hawaii {industry} company"]

        try:
            # Use public LinkedIn company search
            # Note: This uses web scraping. For production, consider LinkedIn API or Sales Navigator
            for query in search_queries[:3]:  # Limit to avoid rate limiting
                companies = await self._search_companies_web(query)
                leads.extend(companies)
                await asyncio.sleep(2)  # Rate limiting

        except Exception as e:
            print(f"LinkedIn scraper error: {e}")

        return leads[:20]  # Return top 20

    async def _search_companies_web(self, query: str) -> List[Dict]:
        """
        Search LinkedIn via web scraping (use with caution - respect robots.txt)
        """
        companies = []

        # For production, you should use:
        # 1. LinkedIn Official API (requires partnership)
        # 2. RapidAPI LinkedIn endpoints
        # 3. Phantombuster LinkedIn scrapers
        # 4. Apify LinkedIn scrapers

        # Placeholder for demonstration - replace with actual API calls
        print(f"Searching LinkedIn for: {query}")

        # Example structure of what real scraping would return
        sample_result = {
            "company_name": f"Sample Company from LinkedIn ({query})",
            "website": "https://example.com",
            "industry": "Technology",
            "employee_count": 150,
            "location": "Honolulu, HI",
            "linkedin_url": "https://linkedin.com/company/example",
            "description": "Sample description from LinkedIn",
            "source": "linkedin"
        }

        # In production, replace with actual LinkedIn API/scraper results
        # companies.append(sample_result)

        return companies


class PacificBusinessNewsScraper:
    """
    Scraper for Pacific Business News (bizjournals.com/pacific)
    Extracts Hawaii business listings, news, and company profiles
    """

    def __init__(self):
        self.base_url = "https://www.bizjournals.com/pacific"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    async def scrape_companies(self, industry: str = None) -> List[Dict]:
        """
        Scrape Pacific Business News for Hawaii companies
        """
        leads = []

        try:
            # PBN sections to scrape
            sections = [
                "/news/technology",
                "/news/health-care",
                "/news/tourism-hospitality",
                "/news/retail",
                "/companies"
            ]

            async with aiohttp.ClientSession() as session:
                for section in sections:
                    url = f"{self.base_url}{section}"
                    companies = await self._scrape_section(session, url)
                    leads.extend(companies)
                    await asyncio.sleep(1)  # Be respectful

        except Exception as e:
            print(f"PBN scraper error: {e}")

        return leads

    async def _scrape_section(self, session: aiohttp.ClientSession, url: str) -> List[Dict]:
        """
        Scrape a specific PBN section for company mentions
        """
        companies = []

        try:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Find company mentions in articles
                    articles = soup.find_all('div', class_=['item', 'article', 'story'])

                    for article in articles[:10]:  # Limit per section
                        company_data = self._extract_company_from_article(article)
                        if company_data:
                            companies.append(company_data)

        except Exception as e:
            print(f"Error scraping {url}: {e}")

        return companies

    def _extract_company_from_article(self, article) -> Optional[Dict]:
        """
        Extract company information from a PBN article
        """
        try:
            # Extract company name from title/content
            title = article.find(['h2', 'h3', 'h4'])
            if not title:
                return None

            title_text = title.get_text(strip=True)

            # Basic company data structure
            return {
                "company_name": self._extract_company_name(title_text),
                "source": "pacific_business_news",
                "article_title": title_text,
                "article_url": article.find('a')['href'] if article.find('a') else None,
                "location": "Hawaii",  # PBN focuses on Hawaii
                "discovered_date": datetime.now().isoformat()
            }

        except Exception as e:
            return None

    def _extract_company_name(self, text: str) -> str:
        """
        Extract company name from article text using patterns
        """
        # Remove common article words
        text = re.sub(r'^(How|Why|What|When|Where)\s+', '', text, flags=re.IGNORECASE)

        # Extract text before common separators
        for separator in ['to open', 'opens', 'closes', 'hires', 'names', 'announces']:
            if separator in text.lower():
                parts = text.split(separator, 1)
                return parts[0].strip()

        return text[:100]  # Fallback


class GoogleBusinessScraper:
    """
    Google Business/Maps scraper using SerpAPI or Outscraper
    Finds Hawaii businesses with detailed information
    """

    def __init__(self, serpapi_key: Optional[str] = None):
        self.serpapi_key = serpapi_key

    async def search_businesses(self, query: str, location: str = "Hawaii") -> List[Dict]:
        """
        Search Google Maps/Business for Hawaii companies

        Args:
            query: Business type (e.g., 'hotels', 'restaurants', 'medical clinics')
            location: Geographic location
        """
        leads = []

        if not self.serpapi_key:
            print("SerpAPI key not provided. Using alternative method...")
            return await self._search_without_api(query, location)

        try:
            # Use SerpAPI for Google Maps results
            search = GoogleSearch({
                "q": f"{query} in {location}",
                "engine": "google_maps",
                "type": "search",
                "api_key": self.serpapi_key
            })

            results = search.get_dict()

            if "local_results" in results:
                for business in results["local_results"][:20]:
                    lead = self._parse_google_business(business)
                    if lead:
                        leads.append(lead)

        except Exception as e:
            print(f"Google Business scraper error: {e}")

        return leads

    async def _search_without_api(self, query: str, location: str) -> List[Dict]:
        """
        Alternative search method without SerpAPI
        Uses direct Google search with parsing
        """
        # This would implement web scraping of Google search results
        # For production, strongly recommend using official APIs
        print(f"Searching Google for: {query} in {location}")
        return []

    def _parse_google_business(self, business_data: Dict) -> Optional[Dict]:
        """
        Parse Google Business data into our lead format
        """
        try:
            return {
                "company_name": business_data.get("title", ""),
                "location": business_data.get("address", ""),
                "phone": business_data.get("phone", ""),
                "website": business_data.get("website", ""),
                "rating": business_data.get("rating", 0),
                "reviews": business_data.get("reviews", 0),
                "category": business_data.get("type", ""),
                "hours": business_data.get("hours", {}),
                "latitude": business_data.get("gps_coordinates", {}).get("latitude"),
                "longitude": business_data.get("gps_coordinates", {}).get("longitude"),
                "source": "google_maps"
            }
        except Exception as e:
            print(f"Error parsing business data: {e}")
            return None


class HawaiiBusinessDirectoryScraper:
    """
    Scraper for Hawaii-specific business directories and chambers of commerce
    """

    def __init__(self):
        self.directories = {
            "chamber_honolulu": "https://www.cochawaii.org/member-directory",
            "hisbdc": "https://hisbdc.org/",
            "htdc": "https://www.htdc.org/portfolio/",
            "hawaii_business": "https://www.hawaiibusiness.com/hawaii-business-directory/"
        }

    async def scrape_all_directories(self) -> List[Dict]:
        """
        Scrape all Hawaii business directories
        """
        all_leads = []

        async with aiohttp.ClientSession() as session:
            tasks = [
                self._scrape_chamber_of_commerce(session),
                self._scrape_htdc_portfolio(session),
                self._scrape_hawaii_business_mag(session)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, list):
                    all_leads.extend(result)

        return all_leads

    async def _scrape_chamber_of_commerce(self, session: aiohttp.ClientSession) -> List[Dict]:
        """
        Scrape Honolulu Chamber of Commerce member directory
        """
        leads = []
        url = self.directories["chamber_honolulu"]

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Parse member listings (structure varies by site)
                    members = soup.find_all('div', class_=['member', 'directory-item', 'business-listing'])

                    for member in members[:30]:
                        lead = self._parse_member_listing(member)
                        if lead:
                            lead["source"] = "honolulu_chamber"
                            leads.append(lead)

        except Exception as e:
            print(f"Error scraping Chamber: {e}")

        return leads

    async def _scrape_htdc_portfolio(self, session: aiohttp.ClientSession) -> List[Dict]:
        """
        Scrape Hawaii Technology Development Corporation portfolio companies
        """
        leads = []
        url = self.directories["htdc"]

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Parse HTDC portfolio companies
                    companies = soup.find_all('div', class_=['portfolio-company', 'company-card'])

                    for company in companies:
                        lead = self._parse_htdc_company(company)
                        if lead:
                            lead["source"] = "htdc_portfolio"
                            lead["industry"] = "Technology"  # HTDC focuses on tech
                            leads.append(lead)

        except Exception as e:
            print(f"Error scraping HTDC: {e}")

        return leads

    async def _scrape_hawaii_business_mag(self, session: aiohttp.ClientSession) -> List[Dict]:
        """
        Scrape Hawaii Business Magazine directory
        """
        leads = []
        url = self.directories["hawaii_business"]

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Parse business listings
                    businesses = soup.find_all('div', class_=['business-item', 'directory-entry'])

                    for business in businesses[:30]:
                        lead = self._parse_business_listing(business)
                        if lead:
                            lead["source"] = "hawaii_business_magazine"
                            leads.append(lead)

        except Exception as e:
            print(f"Error scraping Hawaii Business: {e}")

        return leads

    def _parse_member_listing(self, element) -> Optional[Dict]:
        """
        Parse a chamber member listing
        """
        try:
            name = element.find(['h2', 'h3', 'h4', 'a'])
            if not name:
                return None

            return {
                "company_name": name.get_text(strip=True),
                "location": "Honolulu, HI",  # Chamber members are typically local
                "discovered_date": datetime.now().isoformat()
            }
        except:
            return None

    def _parse_htdc_company(self, element) -> Optional[Dict]:
        """
        Parse an HTDC portfolio company
        """
        try:
            name = element.find(['h2', 'h3', 'h4', 'a'])
            description = element.find('p')

            if not name:
                return None

            return {
                "company_name": name.get_text(strip=True),
                "description": description.get_text(strip=True) if description else "",
                "location": "Hawaii",
                "industry": "Technology",
                "discovered_date": datetime.now().isoformat()
            }
        except:
            return None

    def _parse_business_listing(self, element) -> Optional[Dict]:
        """
        Parse a general business listing
        """
        try:
            name = element.find(['h2', 'h3', 'h4', 'a'])
            if not name:
                return None

            return {
                "company_name": name.get_text(strip=True),
                "location": "Hawaii",
                "discovered_date": datetime.now().isoformat()
            }
        except:
            return None


class YelpScraper:
    """
    Yelp business scraper using SerpAPI Yelp search
    Finds Hawaii businesses with reviews, ratings, and contact info
    """

    def __init__(self, serpapi_key: Optional[str] = None):
        self.serpapi_key = serpapi_key

    async def search_businesses(self, query: str, location: str = "Hawaii") -> List[Dict]:
        """
        Search Yelp for Hawaii businesses

        Args:
            query: Business category (e.g., 'restaurants', 'hotels', 'healthcare')
            location: Geographic location
        """
        leads = []

        if not self.serpapi_key:
            print("SerpAPI key not provided for Yelp. Skipping Yelp search...")
            return []

        try:
            # Use SerpAPI for Yelp search
            search = GoogleSearch({
                "engine": "yelp",
                "find_desc": query,
                "find_loc": location,
                "api_key": self.serpapi_key
            })

            results = search.get_dict()

            if "organic_results" in results:
                for business in results["organic_results"][:25]:
                    lead = self._parse_yelp_business(business)
                    if lead:
                        leads.append(lead)

        except Exception as e:
            print(f"Yelp scraper error: {e}")

        return leads

    def _parse_yelp_business(self, business_data: Dict) -> Optional[Dict]:
        """
        Parse Yelp business data into our lead format
        """
        try:
            # Extract phone number from various formats
            phone = business_data.get("phone", "")

            # Extract address
            address = business_data.get("address", "")
            if isinstance(address, list):
                address = ", ".join(address)

            return {
                "company_name": business_data.get("title", ""),
                "location": address or business_data.get("neighborhood", "Hawaii"),
                "phone": phone,
                "website": business_data.get("website", ""),
                "rating": business_data.get("rating", 0),
                "reviews": business_data.get("reviews", 0),
                "category": business_data.get("categories", [""])[0] if business_data.get("categories") else "",
                "price_range": business_data.get("price", ""),
                "description": business_data.get("snippet", ""),
                "yelp_url": business_data.get("link", ""),
                "source": "yelp"
            }
        except Exception as e:
            print(f"Error parsing Yelp business: {e}")
            return None


class AppleMapsScraper:
    """
    Apple Maps business scraper using SerpAPI Apple Maps search
    Finds Hawaii businesses with location data and contact info
    """

    def __init__(self, serpapi_key: Optional[str] = None):
        self.serpapi_key = serpapi_key

    async def search_businesses(self, query: str, location: str = "Hawaii") -> List[Dict]:
        """
        Search Apple Maps for Hawaii businesses

        Args:
            query: Business category
            location: Geographic location
        """
        leads = []

        if not self.serpapi_key:
            print("SerpAPI key not provided for Apple Maps. Skipping Apple Maps search...")
            return []

        try:
            # Use SerpAPI for Apple Maps search
            search = GoogleSearch({
                "engine": "apple_maps",
                "q": f"{query} in {location}",
                "ll": "21.3099,-157.8581",  # Honolulu coordinates
                "api_key": self.serpapi_key
            })

            results = search.get_dict()

            if "organic_results" in results:
                for business in results["organic_results"][:25]:
                    lead = self._parse_apple_maps_business(business)
                    if lead:
                        leads.append(lead)

        except Exception as e:
            print(f"Apple Maps scraper error: {e}")

        return leads

    def _parse_apple_maps_business(self, business_data: Dict) -> Optional[Dict]:
        """
        Parse Apple Maps business data into our lead format
        """
        try:
            return {
                "company_name": business_data.get("title", ""),
                "location": business_data.get("address", ""),
                "phone": business_data.get("phone", ""),
                "website": business_data.get("website", ""),
                "rating": business_data.get("rating", 0),
                "reviews": business_data.get("reviews", 0),
                "category": business_data.get("type", ""),
                "hours": business_data.get("hours", ""),
                "latitude": business_data.get("gps_coordinates", {}).get("latitude"),
                "longitude": business_data.get("gps_coordinates", {}).get("longitude"),
                "source": "apple_maps"
            }
        except Exception as e:
            print(f"Error parsing Apple Maps business: {e}")
            return None


class BBBScraper:
    """
    Better Business Bureau scraper for Hawaii businesses
    Provides business credibility and accreditation data
    """

    def __init__(self):
        self.base_url = "https://www.bbb.org"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    async def search_businesses(self, query: str = "", location: str = "HI") -> List[Dict]:
        """
        Search Better Business Bureau for Hawaii businesses
        """
        leads = []

        try:
            # BBB search URL for Hawaii
            search_url = f"{self.base_url}/search"
            params = {
                "find_text": query,
                "find_loc": location,
                "find_type": "Business"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')

                        # Parse BBB business listings
                        businesses = soup.find_all('div', class_=['result-item', 'business-result'])

                        for business in businesses[:20]:
                            lead = self._parse_bbb_business(business)
                            if lead:
                                leads.append(lead)

        except Exception as e:
            print(f"BBB scraper error: {e}")

        return leads

    def _parse_bbb_business(self, element) -> Optional[Dict]:
        """
        Parse BBB business listing
        """
        try:
            name_elem = element.find(['h3', 'h4', 'a'])
            if not name_elem:
                return None

            rating_elem = element.find(class_=['bbb-rating', 'rating'])
            accredited = element.find(class_='accredited')

            return {
                "company_name": name_elem.get_text(strip=True),
                "bbb_rating": rating_elem.get_text(strip=True) if rating_elem else None,
                "bbb_accredited": bool(accredited),
                "location": "Hawaii",
                "source": "better_business_bureau"
            }
        except:
            return None


class TripAdvisorScraper:
    """
    TripAdvisor scraper for Hawaii tourism and hospitality businesses
    Excellent source for hotels, restaurants, attractions, and tours
    """

    def __init__(self, serpapi_key: Optional[str] = None):
        self.serpapi_key = serpapi_key
        self.base_url = "https://www.tripadvisor.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    async def search_businesses(self, query: str = "hotels", location: str = "Hawaii") -> List[Dict]:
        """
        Search TripAdvisor for Hawaii tourism businesses
        """
        leads = []

        try:
            # Search TripAdvisor (web scraping approach)
            search_url = f"{self.base_url}/Search"
            params = {
                "q": f"{query} {location}",
                "geo": "60971"  # Hawaii geo code
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')

                        # Parse TripAdvisor listings
                        businesses = soup.find_all('div', class_=['result-item', 'listing'])

                        for business in businesses[:20]:
                            lead = self._parse_tripadvisor_business(business)
                            if lead:
                                leads.append(lead)

        except Exception as e:
            print(f"TripAdvisor scraper error: {e}")

        return leads

    def _parse_tripadvisor_business(self, element) -> Optional[Dict]:
        """
        Parse TripAdvisor business listing
        """
        try:
            name_elem = element.find(['h3', 'h4', 'a'])
            if not name_elem:
                return None

            rating_elem = element.find(class_=['rating', 'ui_bubble_rating'])
            reviews_elem = element.find(class_=['review_count', 'reviewCount'])

            return {
                "company_name": name_elem.get_text(strip=True),
                "rating": self._extract_rating(rating_elem) if rating_elem else 0,
                "reviews": self._extract_review_count(reviews_elem) if reviews_elem else 0,
                "location": "Hawaii",
                "industry": "Tourism & Hospitality",
                "source": "tripadvisor"
            }
        except:
            return None

    def _extract_rating(self, element) -> float:
        """Extract rating from TripAdvisor element"""
        try:
            # TripAdvisor uses bubble ratings (e.g., "bubble_50" for 5.0)
            class_str = str(element.get('class', []))
            match = re.search(r'bubble_(\d+)', class_str)
            if match:
                return float(match.group(1)) / 10
            return 0.0
        except:
            return 0.0

    def _extract_review_count(self, element) -> int:
        """Extract review count from element"""
        try:
            text = element.get_text()
            match = re.search(r'(\d+)', text)
            if match:
                return int(match.group(1))
            return 0
        except:
            return 0


class RealLeadDiscoveryOrchestrator:
    """
    Orchestrates all scrapers to discover real Hawaii business leads
    """

    def __init__(self, linkedin_api_key=None, serpapi_key=None):
        self.linkedin_scraper = LinkedInScraper(linkedin_api_key)
        self.pbn_scraper = PacificBusinessNewsScraper()
        self.google_scraper = GoogleBusinessScraper(serpapi_key)
        self.directory_scraper = HawaiiBusinessDirectoryScraper()
        self.yelp_scraper = YelpScraper(serpapi_key)
        self.apple_maps_scraper = AppleMapsScraper(serpapi_key)
        self.bbb_scraper = BBBScraper()
        self.tripadvisor_scraper = TripAdvisorScraper(serpapi_key)

    async def discover_leads(
        self,
        industry: Optional[str] = None,
        location: str = "Hawaii",
        island: Optional[str] = None,
        business_type: Optional[str] = None,
        min_employees: Optional[int] = None,
        max_employees: Optional[int] = None,
        max_leads: int = 50
    ) -> List[Dict]:
        """
        Discover real business leads from all sources with advanced filtering

        Args:
            industry: Target industry filter (e.g., 'tourism', 'healthcare', 'technology')
            location: Geographic location (default: "Hawaii")
            island: Specific Hawaiian island (e.g., 'Oahu', 'Maui', 'Kauai', 'Big Island', 'Molokai', 'Lanai')
            business_type: Type of business (e.g., 'hotel', 'restaurant', 'clinic', 'retail')
            min_employees: Minimum employee count
            max_employees: Maximum employee count
            max_leads: Maximum number of leads to return
        """
        print("🔍 Starting real lead discovery across multiple sources...")

        # Build location string with island if specified
        search_location = location
        if island:
            island_locations = {
                'oahu': 'Oahu, Hawaii',
                'maui': 'Maui, Hawaii',
                'kauai': 'Kauai, Hawaii',
                'big island': 'Big Island, Hawaii',
                'hawaii': 'Big Island, Hawaii',  # Alias for Big Island
                'molokai': 'Molokai, Hawaii',
                'lanai': 'Lanai, Hawaii'
            }
            search_location = island_locations.get(island.lower(), f"{island}, Hawaii")
            print(f"🏝️  Searching on: {search_location}")

        # Determine search query based on filters
        search_query = business_type or industry or "businesses"

        all_leads = []

        # Run all scrapers in parallel
        tasks = [
            self._discover_from_linkedin(industry, search_location),
            self._discover_from_pbn(industry),
            self._discover_from_google(search_query, search_location),
            self._discover_from_directories(),
            self._discover_from_yelp(search_query, search_location),
            self._discover_from_apple_maps(search_query, search_location),
            self._discover_from_bbb(search_query, "HI"),
            self._discover_from_tripadvisor(search_query, search_location)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results
        source_names = [
            "LinkedIn",
            "Pacific Business News",
            "Google Maps",
            "Hawaii Directories",
            "Yelp",
            "Apple Maps",
            "Better Business Bureau",
            "TripAdvisor"
        ]

        for i, result in enumerate(results):
            if isinstance(result, list):
                print(f"✓ {source_names[i]}: Found {len(result)} leads")
                all_leads.extend(result)
            elif isinstance(result, Exception):
                print(f"✗ {source_names[i]}: Error - {str(result)}")

        # Apply filters
        filtered_leads = self._filter_leads(
            all_leads,
            industry=industry,
            island=island,
            business_type=business_type,
            min_employees=min_employees,
            max_employees=max_employees
        )

        # Deduplicate leads by company name
        unique_leads = self._deduplicate_leads(filtered_leads)

        print(f"\n✓ Total unique leads discovered: {len(unique_leads)}")

        return unique_leads[:max_leads]

    async def _discover_from_linkedin(self, industry: Optional[str], location: str) -> List[Dict]:
        """Discover leads from LinkedIn"""
        try:
            return await self.linkedin_scraper.search_hawaii_companies(industry)
        except Exception as e:
            print(f"LinkedIn discovery error: {e}")
            return []

    async def _discover_from_pbn(self, industry: Optional[str]) -> List[Dict]:
        """Discover leads from Pacific Business News"""
        try:
            return await self.pbn_scraper.scrape_companies(industry)
        except Exception as e:
            print(f"PBN discovery error: {e}")
            return []

    async def _discover_from_google(self, query: str, location: str) -> List[Dict]:
        """Discover leads from Google Business"""
        try:
            results = await self.google_scraper.search_businesses(query, location)
            return results
        except Exception as e:
            print(f"Google discovery error: {e}")
            return []

    async def _discover_from_directories(self) -> List[Dict]:
        """Discover leads from Hawaii business directories"""
        try:
            return await self.directory_scraper.scrape_all_directories()
        except Exception as e:
            print(f"Directory discovery error: {e}")
            return []

    async def _discover_from_yelp(self, query: str, location: str) -> List[Dict]:
        """Discover leads from Yelp"""
        try:
            return await self.yelp_scraper.search_businesses(query, location)
        except Exception as e:
            print(f"Yelp discovery error: {e}")
            return []

    async def _discover_from_apple_maps(self, query: str, location: str) -> List[Dict]:
        """Discover leads from Apple Maps"""
        try:
            return await self.apple_maps_scraper.search_businesses(query, location)
        except Exception as e:
            print(f"Apple Maps discovery error: {e}")
            return []

    async def _discover_from_bbb(self, query: str, location: str) -> List[Dict]:
        """Discover leads from Better Business Bureau"""
        try:
            return await self.bbb_scraper.search_businesses(query, location)
        except Exception as e:
            print(f"BBB discovery error: {e}")
            return []

    async def _discover_from_tripadvisor(self, query: str, location: str) -> List[Dict]:
        """Discover leads from TripAdvisor"""
        try:
            return await self.tripadvisor_scraper.search_businesses(query, location)
        except Exception as e:
            print(f"TripAdvisor discovery error: {e}")
            return []

    def _filter_leads(
        self,
        leads: List[Dict],
        industry: Optional[str] = None,
        island: Optional[str] = None,
        business_type: Optional[str] = None,
        min_employees: Optional[int] = None,
        max_employees: Optional[int] = None
    ) -> List[Dict]:
        """
        Filter leads based on criteria

        Args:
            leads: List of lead dictionaries
            industry: Filter by industry
            island: Filter by island location
            business_type: Filter by business type/category
            min_employees: Minimum employee count
            max_employees: Maximum employee count
        """
        filtered = leads

        if island:
            island_lower = island.lower()
            island_keywords = {
                'oahu': ['oahu', 'honolulu', 'pearl city', 'kaneohe', 'kailua'],
                'maui': ['maui', 'kahului', 'lahaina', 'kihei', 'wailea'],
                'kauai': ['kauai', 'lihue', 'kapaa', 'poipu', 'princeville'],
                'big island': ['big island', 'hilo', 'kona', 'kailua-kona', 'waimea'],
                'hawaii': ['big island', 'hilo', 'kona', 'kailua-kona', 'waimea'],
                'molokai': ['molokai', 'kaunakakai'],
                'lanai': ['lanai', 'lanai city']
            }

            keywords = island_keywords.get(island_lower, [island_lower])
            filtered = [
                lead for lead in filtered
                if any(keyword in lead.get('location', '').lower() for keyword in keywords)
            ]

        if industry:
            industry_lower = industry.lower()
            filtered = [
                lead for lead in filtered
                if industry_lower in lead.get('industry', '').lower() or
                   industry_lower in lead.get('category', '').lower() or
                   industry_lower in lead.get('description', '').lower()
            ]

        if business_type:
            type_lower = business_type.lower()
            filtered = [
                lead for lead in filtered
                if type_lower in lead.get('category', '').lower() or
                   type_lower in lead.get('company_name', '').lower() or
                   type_lower in lead.get('description', '').lower()
            ]

        if min_employees is not None:
            filtered = [
                lead for lead in filtered
                if lead.get('employee_count', 1) >= min_employees
            ]

        if max_employees is not None:
            filtered = [
                lead for lead in filtered
                if lead.get('employee_count', float('inf')) <= max_employees
            ]

        return filtered

    def _deduplicate_leads(self, leads: List[Dict]) -> List[Dict]:
        """
        Remove duplicate leads based on company name similarity
        """
        seen_companies = set()
        unique_leads = []

        for lead in leads:
            company_name = lead.get("company_name", "").lower().strip()

            # Basic deduplication - can be enhanced with fuzzy matching
            if company_name and company_name not in seen_companies:
                seen_companies.add(company_name)
                unique_leads.append(lead)

        return unique_leads


# Example usage
async def main():
    """
    Example usage of the real lead discovery system
    """
    # Initialize orchestrator (add your API keys)
    orchestrator = RealLeadDiscoveryOrchestrator(
        linkedin_api_key=None,  # Add LinkedIn API key if available
        serpapi_key=None  # Add SerpAPI key for Google Maps scraping
    )

    # Discover leads
    leads = await orchestrator.discover_leads(
        industry="tourism",
        location="Hawaii",
        max_leads=50
    )

    print(f"\nDiscovered {len(leads)} leads:")
    for lead in leads[:5]:
        print(f"- {lead.get('company_name')} ({lead.get('source')})")


if __name__ == "__main__":
    asyncio.run(main())
