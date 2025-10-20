"""
Query Manager - Intelligently rotates search queries to discover new leads
without repeating the same searches and wasting API calls
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import random


class QueryRotationManager:
    """
    Manages query rotation to ensure we don't repeat the same searches
    and discover truly new leads each day
    """

    def __init__(self, state_file: str = "query_rotation_state.json"):
        self.state_file = state_file
        self.state = self._load_state()

        # Define comprehensive query variations for Hawaii businesses
        self.query_templates = {
            "location": [
                "Honolulu", "Oahu", "Maui", "Kauai", "Big Island", "Hawaii Island",
                "Waikiki", "Lahaina", "Kailua-Kona", "Hilo", "Kihei", "Waipahu",
                "Pearl City", "Kaneohe", "Kapolei", "Aiea", "Mililani", "Kahului"
            ],
            "industry_keywords": {
                "hospitality": [
                    "hotel", "resort", "vacation rental", "bed and breakfast",
                    "inn", "lodge", "hostel", "accommodation", "beachfront hotel",
                    "boutique hotel", "luxury resort", "timeshare"
                ],
                "tourism": [
                    "tour operator", "activity provider", "tour company",
                    "excursion", "sightseeing", "adventure tours", "snorkeling",
                    "luau", "boat tours", "helicopter tours", "zipline"
                ],
                "restaurant": [
                    "restaurant", "cafe", "coffee shop", "bar", "food truck",
                    "catering", "bakery", "dining", "fast food", "fine dining",
                    "seafood restaurant", "asian restaurant", "breakfast spot"
                ],
                "retail": [
                    "shop", "boutique", "store", "retail", "gift shop",
                    "clothing store", "jewelry store", "souvenir shop",
                    "surf shop", "art gallery", "marketplace"
                ],
                "healthcare": [
                    "medical clinic", "dental office", "healthcare provider",
                    "physical therapy", "urgent care", "wellness center",
                    "chiropractic", "medical practice", "health clinic"
                ],
                "professional_services": [
                    "law firm", "accounting firm", "consulting", "insurance agency",
                    "real estate", "marketing agency", "financial advisor",
                    "business services", "property management", "tax services"
                ],
                "wellness": [
                    "spa", "massage", "yoga studio", "fitness center", "gym",
                    "wellness spa", "beauty salon", "day spa", "health club"
                ],
                "construction": [
                    "contractor", "construction company", "builder",
                    "home improvement", "remodeling", "roofing", "plumbing",
                    "electrical contractor", "landscaping"
                ],
                "education": [
                    "school", "tutoring", "training center", "daycare",
                    "preschool", "education center", "learning center"
                ]
            },
            "modifiers": [
                "business", "company", "service", "provider", "professional",
                "local", "island", "hawaiian", "best", "top rated"
            ]
        }

    def _load_state(self) -> Dict:
        """Load query rotation state"""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "queries_used": [],  # List of queries already executed
                "last_rotation": None,
                "source_exhaustion": {},  # source -> exhaustion_level (0-100)
                "industry_rotation": {},  # industry -> last_used_index
                "location_rotation": {},  # location -> last_used_index
            }

    def _save_state(self):
        """Save query rotation state"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2, default=str)

    def get_next_queries(
        self,
        industry: Optional[str] = None,
        location: Optional[str] = None,
        max_queries: int = 5
    ) -> List[str]:
        """
        Get the next set of queries to use, rotating through variations
        to discover new leads without repeating previous searches

        Returns: List of query strings to use for this discovery session
        """
        queries = []

        # Determine industries to search
        if industry:
            industries = [industry.lower()]
        else:
            # Rotate through all industries
            industries = list(self.query_templates["industry_keywords"].keys())
            # Prioritize industries we haven't searched recently
            industries = self._prioritize_unexhausted(industries, "industry")

        # Determine locations to search
        if location:
            locations = [loc for loc in self.query_templates["location"]
                        if location.lower() in loc.lower()]
            if not locations:
                locations = [location]
        else:
            # Rotate through locations, prioritizing less-searched areas
            locations = self.query_templates["location"][:8]  # Top 8 locations
            locations = self._prioritize_unexhausted(locations, "location")

        # Generate diverse queries
        for ind in industries[:3]:  # Max 3 industries per run
            keywords = self.query_templates["industry_keywords"].get(ind, [ind])

            # Get next keyword variation for this industry
            rotation_idx = self.state.get("industry_rotation", {}).get(ind, 0)
            keyword = keywords[rotation_idx % len(keywords)]

            # Update rotation index
            if "industry_rotation" not in self.state:
                self.state["industry_rotation"] = {}
            self.state["industry_rotation"][ind] = (rotation_idx + 1) % len(keywords)

            for loc in locations[:2]:  # Max 2 locations per industry
                # Build query variations
                base_query = f"{loc} {keyword}"

                # Skip if we've used this exact query recently
                if self._was_query_used_recently(base_query, days=7):
                    continue

                queries.append(base_query)

                if len(queries) >= max_queries:
                    break

            if len(queries) >= max_queries:
                break

        # If we didn't get enough queries (all were recent), use modifiers
        if len(queries) < max_queries:
            for ind in industries:
                keywords = self.query_templates["industry_keywords"].get(ind, [ind])
                keyword = random.choice(keywords)
                loc = random.choice(locations)
                modifier = random.choice(self.query_templates["modifiers"])

                query = f"{modifier} {keyword} {loc}"
                if not self._was_query_used_recently(query, days=7):
                    queries.append(query)

                if len(queries) >= max_queries:
                    break

        # Mark queries as used
        for query in queries:
            self._mark_query_used(query)

        self._save_state()
        return queries

    def _prioritize_unexhausted(
        self,
        items: List[str],
        category: str
    ) -> List[str]:
        """
        Sort items by exhaustion level (least exhausted first)
        """
        exhaustion_key = f"{category}_exhaustion"
        exhaustion = self.state.get(exhaustion_key, {})

        # Sort by exhaustion level (ascending)
        return sorted(items, key=lambda x: exhaustion.get(x.lower(), 0))

    def _was_query_used_recently(self, query: str, days: int = 7) -> bool:
        """Check if a query was used in the last N days"""
        queries_used = self.state.get("queries_used", [])

        cutoff_date = datetime.now() - timedelta(days=days)

        for entry in queries_used:
            if isinstance(entry, dict):
                if (entry.get("query", "").lower() == query.lower() and
                    datetime.fromisoformat(entry["used_at"]) > cutoff_date):
                    return True
            elif isinstance(entry, str) and entry.lower() == query.lower():
                # Legacy format, assume it's recent
                return True

        return False

    def _mark_query_used(self, query: str):
        """Mark a query as used"""
        if "queries_used" not in self.state:
            self.state["queries_used"] = []

        self.state["queries_used"].append({
            "query": query,
            "used_at": datetime.now().isoformat()
        })

        # Keep only last 100 queries to prevent state file from growing too large
        self.state["queries_used"] = self.state["queries_used"][-100:]

    def mark_source_results(
        self,
        source: str,
        total_found: int,
        duplicates: int,
        added: int
    ):
        """
        Track source effectiveness and mark as exhausted if needed

        Args:
            source: Source name (e.g., "google_maps", "yelp")
            total_found: Total results returned
            duplicates: Number of duplicates found
            added: Number of new leads actually added
        """
        if "source_exhaustion" not in self.state:
            self.state["source_exhaustion"] = {}

        # Calculate exhaustion percentage
        if total_found > 0:
            duplicate_rate = (duplicates / total_found) * 100
        else:
            duplicate_rate = 100  # No results = exhausted

        # Update exhaustion level (weighted average)
        current_exhaustion = self.state["source_exhaustion"].get(source, 0)
        new_exhaustion = (current_exhaustion * 0.7) + (duplicate_rate * 0.3)

        self.state["source_exhaustion"][source] = min(new_exhaustion, 100)

        # Also track last check time
        self.state["source_exhaustion"][f"{source}_last_check"] = datetime.now().isoformat()

        self._save_state()

    def get_recommended_sources(self, max_sources: int = 5) -> List[str]:
        """
        Get recommended sources to check, prioritizing less exhausted ones
        """
        all_sources = [
            "google_maps",
            "yelp",
            "linkedin",
            "pacific_business_news",
            "hawaii_directories",
            "apple_maps",
            "better_business_bureau",
            "tripadvisor"
        ]

        exhaustion = self.state.get("source_exhaustion", {})

        # Sort sources by exhaustion level (least exhausted first)
        sorted_sources = sorted(
            all_sources,
            key=lambda s: exhaustion.get(s, 0)
        )

        return sorted_sources[:max_sources]

    def should_use_source(self, source: str, threshold: float = 80.0) -> bool:
        """
        Determine if a source should be used based on exhaustion level

        Returns False if source is too exhausted (>80% duplicate rate)
        """
        exhaustion = self.state.get("source_exhaustion", {}).get(source, 0)

        # Check if source has recovered (24 hours since last check)
        last_check = self.state.get("source_exhaustion", {}).get(f"{source}_last_check")
        if last_check:
            last_check_time = datetime.fromisoformat(last_check)
            if datetime.now() - last_check_time > timedelta(hours=24):
                # Reset exhaustion by 50% after 24 hours
                self.state["source_exhaustion"][source] = exhaustion * 0.5
                self._save_state()
                exhaustion = self.state["source_exhaustion"][source]

        return exhaustion < threshold

    def get_diversified_parameters(
        self,
        user_industry: Optional[str] = None,
        user_location: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        Get diversified search parameters that rotate through options
        to discover new leads without repeating searches

        Returns dict with industries and locations to search
        """
        # Get next queries
        queries = self.get_next_queries(
            industry=user_industry,
            location=user_location,
            max_queries=5
        )

        # Extract industries and locations from queries
        industries = []
        locations = []

        for query in queries:
            query_lower = query.lower()

            # Find industry
            for ind, keywords in self.query_templates["industry_keywords"].items():
                if any(kw in query_lower for kw in keywords):
                    if ind not in industries:
                        industries.append(ind)
                    break

            # Find location
            for loc in self.query_templates["location"]:
                if loc.lower() in query_lower:
                    if loc not in locations:
                        locations.append(loc)
                    break

        return {
            "queries": queries,
            "industries": industries or [user_industry] if user_industry else [],
            "locations": locations or [user_location] if user_location else [],
            "recommended_sources": self.get_recommended_sources()
        }

    def get_stats(self) -> Dict:
        """Get query rotation statistics"""
        return {
            "total_queries_used": len(self.state.get("queries_used", [])),
            "recent_queries": [
                q.get("query") if isinstance(q, dict) else q
                for q in self.state.get("queries_used", [])[-10:]
            ],
            "source_exhaustion": self.state.get("source_exhaustion", {}),
            "industry_rotation": self.state.get("industry_rotation", {}),
        }


# Global instance
_query_manager_instance: Optional[QueryRotationManager] = None


def get_query_manager() -> QueryRotationManager:
    """Get or create the global query manager instance"""
    global _query_manager_instance

    if _query_manager_instance is None:
        _query_manager_instance = QueryRotationManager()

    return _query_manager_instance
