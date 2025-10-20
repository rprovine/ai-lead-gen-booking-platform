"""
ICP (Ideal Customer Profile) Manager and Smart Lead Discovery System

Handles:
- ICP criteria definition and scoring
- Discovery state management (avoid re-scraping)
- API response caching
- Daily limit tracking and enforcement
- Smart lead prioritization
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import asyncio


@dataclass
class ICPCriteria:
    """Defines the Ideal Customer Profile for LeniLani"""

    # Industry preferences (industry -> weight)
    preferred_industries: Dict[str, float] = None

    # Location preferences (location -> weight)
    preferred_locations: Dict[str, float] = None

    # Company size (employee count ranges -> weight)
    preferred_company_sizes: Dict[str, float] = None

    # Pain points that indicate good fit
    key_pain_points: List[str] = None

    # Technology adoption indicators
    tech_indicators: List[str] = None

    # Minimum score threshold
    min_score_threshold: float = 70.0

    def __post_init__(self):
        """Initialize default ICP criteria for LeniLani"""
        if self.preferred_industries is None:
            self.preferred_industries = {
                # High-value industries for AI/ML consulting in Hawaii
                "tourism": 25.0,
                "hospitality": 25.0,
                "healthcare": 20.0,
                "retail": 15.0,
                "finance": 20.0,
                "real_estate": 15.0,
                "professional_services": 15.0,
                "education": 12.0,
                "government": 10.0,
                "construction": 10.0,
                "agriculture": 8.0,
            }

        if self.preferred_locations is None:
            self.preferred_locations = {
                # Hawaii locations (all good, some slightly better)
                "honolulu": 15.0,
                "oahu": 15.0,
                "maui": 12.0,
                "kauai": 12.0,
                "big_island": 12.0,
                "hawaii": 10.0,  # General Hawaii
            }

        if self.preferred_company_sizes is None:
            self.preferred_company_sizes = {
                # Sweet spot for consulting: 10-500 employees
                "10-50": 20.0,      # Small-medium, high growth potential
                "51-100": 25.0,     # Medium, perfect fit
                "101-250": 25.0,    # Medium-large, great fit
                "251-500": 20.0,    # Large, good budget
                "501-1000": 10.0,   # Enterprise, may have in-house
                "1000+": 5.0,       # Very large, likely has tech team
                "1-10": 5.0,        # Too small, limited budget
            }

        if self.key_pain_points is None:
            self.key_pain_points = [
                "manual processes",
                "data analysis",
                "customer experience",
                "automation",
                "efficiency",
                "digital transformation",
                "competitive advantage",
                "operational costs",
                "scaling challenges",
                "customer insights",
                "personalization",
                "predictive analytics",
            ]

        if self.tech_indicators is None:
            self.tech_indicators = [
                "website",
                "online booking",
                "mobile app",
                "ecommerce",
                "crm",
                "digital marketing",
                "social media",
                "cloud",
                "api",
                "integration",
            ]


class DiscoveryStateManager:
    """Manages discovery session state to avoid re-scraping and maintain continuity"""

    def __init__(self):
        self.state_file = "discovery_state.json"
        self.state: Dict[str, Any] = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load discovery state from disk"""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "last_discovery": None,
                "sources_checked": {},  # source -> {last_check, queries_executed}
                "seen_companies": set(),  # Company names we've seen
                "filtered_companies": set(),  # Companies that didn't meet ICP
                "daily_stats": {},  # date -> {leads_added, api_calls}
            }

    def _save_state(self):
        """Save discovery state to disk"""
        # Convert sets to lists for JSON serialization
        state_copy = self.state.copy()
        if isinstance(state_copy.get("seen_companies"), set):
            state_copy["seen_companies"] = list(state_copy["seen_companies"])
        if isinstance(state_copy.get("filtered_companies"), set):
            state_copy["filtered_companies"] = list(state_copy["filtered_companies"])

        with open(self.state_file, 'w') as f:
            json.dump(state_copy, f, indent=2, default=str)

    def mark_company_seen(self, company_name: str):
        """Mark a company as seen (discovered)"""
        if isinstance(self.state.get("seen_companies"), list):
            self.state["seen_companies"] = set(self.state["seen_companies"])
        self.state["seen_companies"].add(company_name.lower().strip())
        self._save_state()

    def mark_company_filtered(self, company_name: str):
        """Mark a company as filtered out (didn't meet ICP)"""
        if isinstance(self.state.get("filtered_companies"), list):
            self.state["filtered_companies"] = set(self.state["filtered_companies"])
        self.state["filtered_companies"].add(company_name.lower().strip())
        self._save_state()

    def is_company_seen(self, company_name: str) -> bool:
        """Check if company has been seen before"""
        if isinstance(self.state.get("seen_companies"), list):
            self.state["seen_companies"] = set(self.state["seen_companies"])
        return company_name.lower().strip() in self.state.get("seen_companies", set())

    def is_company_filtered(self, company_name: str) -> bool:
        """Check if company was previously filtered out"""
        if isinstance(self.state.get("filtered_companies"), list):
            self.state["filtered_companies"] = set(self.state["filtered_companies"])
        return company_name.lower().strip() in self.state.get("filtered_companies", set())

    def mark_source_checked(self, source: str, query: str):
        """Mark a source/query combination as checked"""
        if "sources_checked" not in self.state:
            self.state["sources_checked"] = {}

        if source not in self.state["sources_checked"]:
            self.state["sources_checked"][source] = {
                "last_check": datetime.now().isoformat(),
                "queries_executed": []
            }

        if query not in self.state["sources_checked"][source]["queries_executed"]:
            self.state["sources_checked"][source]["queries_executed"].append(query)

        self.state["sources_checked"][source]["last_check"] = datetime.now().isoformat()
        self._save_state()

    def should_check_source(self, source: str, query: str, hours_threshold: int = 24) -> bool:
        """Determine if we should check this source/query (based on last check time)"""
        if source not in self.state.get("sources_checked", {}):
            return True

        source_data = self.state["sources_checked"][source]

        # If query hasn't been executed, check it
        if query not in source_data.get("queries_executed", []):
            return True

        # Check if enough time has passed
        last_check = datetime.fromisoformat(source_data["last_check"])
        time_since = datetime.now() - last_check

        return time_since > timedelta(hours=hours_threshold)

    def get_daily_stats(self, date: Optional[str] = None) -> Dict[str, int]:
        """Get stats for a specific date (defaults to today)"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        return self.state.get("daily_stats", {}).get(date, {
            "leads_added": 0,
            "api_calls": 0,
        })

    def increment_daily_leads(self, count: int = 1):
        """Increment the daily lead count"""
        today = datetime.now().strftime("%Y-%m-%d")

        if "daily_stats" not in self.state:
            self.state["daily_stats"] = {}

        if today not in self.state["daily_stats"]:
            self.state["daily_stats"][today] = {"leads_added": 0, "api_calls": 0}

        self.state["daily_stats"][today]["leads_added"] += count
        self._save_state()

    def increment_api_calls(self, count: int = 1):
        """Increment the daily API call count"""
        today = datetime.now().strftime("%Y-%m-%d")

        if "daily_stats" not in self.state:
            self.state["daily_stats"] = {}

        if today not in self.state["daily_stats"]:
            self.state["daily_stats"][today] = {"leads_added": 0, "api_calls": 0}

        self.state["daily_stats"][today]["api_calls"] += count
        self._save_state()

    def reset_daily_stats(self):
        """Reset daily stats (should be called at midnight)"""
        # Keep last 30 days of history
        cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        if "daily_stats" in self.state:
            self.state["daily_stats"] = {
                k: v for k, v in self.state["daily_stats"].items()
                if k >= cutoff_date
            }

        self._save_state()


class APIResponseCache:
    """Simple in-memory cache for API responses with TTL"""

    def __init__(self, default_ttl_hours: int = 24):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = timedelta(hours=default_ttl_hours)

    def _generate_key(self, service: str, params: Dict[str, Any]) -> str:
        """Generate cache key from service and parameters"""
        param_str = json.dumps(params, sort_keys=True)
        return f"{service}:{hashlib.md5(param_str.encode()).hexdigest()}"

    def get(self, service: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached response if available and not expired"""
        key = self._generate_key(service, params)

        if key not in self.cache:
            return None

        entry = self.cache[key]

        # Check if expired
        if datetime.now() > entry["expires_at"]:
            del self.cache[key]
            return None

        return entry["data"]

    def set(self, service: str, params: Dict[str, Any], data: Any, ttl_hours: Optional[int] = None):
        """Set cache entry with TTL"""
        key = self._generate_key(service, params)
        ttl = timedelta(hours=ttl_hours) if ttl_hours else self.default_ttl

        self.cache[key] = {
            "data": data,
            "cached_at": datetime.now(),
            "expires_at": datetime.now() + ttl,
        }

    def clear_expired(self):
        """Remove all expired entries"""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now > entry["expires_at"]
        ]

        for key in expired_keys:
            del self.cache[key]

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = datetime.now()
        active_entries = sum(1 for entry in self.cache.values() if now <= entry["expires_at"])

        return {
            "total_entries": len(self.cache),
            "active_entries": active_entries,
            "expired_entries": len(self.cache) - active_entries,
        }


class SmartLeadDiscoveryManager:
    """
    Manages smart lead discovery with ICP prioritization, deduplication,
    and continuity across sessions
    """

    def __init__(
        self,
        icp_criteria: Optional[ICPCriteria] = None,
        daily_limit: int = 50,
        api_cache_ttl_hours: int = 24,
    ):
        self.icp = icp_criteria or ICPCriteria()
        self.daily_limit = daily_limit
        self.state_manager = DiscoveryStateManager()
        self.api_cache = APIResponseCache(default_ttl_hours=api_cache_ttl_hours)

    def calculate_icp_score(self, lead: Dict[str, Any]) -> float:
        """
        Calculate ICP fit score for a lead (0-100)

        Returns higher score for better ICP matches
        """
        score = 50.0  # Base score

        # Industry match (0-25 points)
        industry = lead.get("industry", "").lower()
        for pref_industry, weight in self.icp.preferred_industries.items():
            if pref_industry in industry:
                score += weight
                break

        # Location match (0-15 points)
        location = lead.get("location", "").lower()
        for pref_location, weight in self.icp.preferred_locations.items():
            if pref_location in location:
                score += weight
                break

        # Company size match (0-25 points)
        employee_count = lead.get("employee_count", 0)
        size_category = self._categorize_company_size(employee_count)
        score += self.icp.preferred_company_sizes.get(size_category, 0)

        # Pain points match (0-15 points)
        description = (lead.get("description", "") + " " + lead.get("notes", "")).lower()
        pain_point_matches = sum(
            1 for pain_point in self.icp.key_pain_points
            if pain_point in description
        )
        score += min(pain_point_matches * 3, 15)

        # Tech indicators (0-10 points)
        tech_matches = sum(
            1 for indicator in self.icp.tech_indicators
            if indicator in description or indicator in lead.get("website", "").lower()
        )
        score += min(tech_matches * 2, 10)

        # Website presence (+5 points - important for digital maturity)
        if lead.get("website"):
            score += 5

        # Contact info completeness (+5 points)
        if lead.get("email") or lead.get("phone"):
            score += 5

        return min(score, 100.0)

    def _categorize_company_size(self, employee_count: int) -> str:
        """Categorize company by employee count"""
        if employee_count >= 1000:
            return "1000+"
        elif employee_count >= 501:
            return "501-1000"
        elif employee_count >= 251:
            return "251-500"
        elif employee_count >= 101:
            return "101-250"
        elif employee_count >= 51:
            return "51-100"
        elif employee_count >= 10:
            return "10-50"
        else:
            return "1-10"

    def can_add_leads_today(self, count: int = 1) -> bool:
        """Check if we can add more leads today (within daily limit)"""
        stats = self.state_manager.get_daily_stats()
        current_count = stats.get("leads_added", 0)
        return current_count + count <= self.daily_limit

    def get_remaining_daily_capacity(self) -> int:
        """Get remaining number of leads that can be added today"""
        stats = self.state_manager.get_daily_stats()
        current_count = stats.get("leads_added", 0)
        return max(0, self.daily_limit - current_count)

    def filter_and_prioritize_leads(
        self,
        discovered_leads: List[Dict[str, Any]],
        existing_leads: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Filter and prioritize discovered leads:
        1. Remove duplicates (already seen/filtered)
        2. Remove leads that don't meet ICP threshold
        3. Score remaining leads
        4. Sort by ICP score (best first)
        5. Limit to daily capacity

        Returns: Prioritized list of leads ready to add
        """
        if existing_leads is None:
            existing_leads = []

        # Build deduplication sets from existing leads
        existing_names = {
            self._normalize_company_name(lead.get("company_name", ""))
            for lead in existing_leads
        }
        existing_websites = {
            self._normalize_website(lead.get("website", ""))
            for lead in existing_leads
            if lead.get("website")
        }
        existing_phones = {
            self._normalize_phone(lead.get("phone", ""))
            for lead in existing_leads
            if lead.get("phone")
        }

        filtered_leads = []

        for lead in discovered_leads:
            company_name = lead.get("company_name", "")
            normalized_name = self._normalize_company_name(company_name)

            # Skip if already in database
            if normalized_name in existing_names:
                continue

            # Skip if website already exists
            if lead.get("website"):
                normalized_website = self._normalize_website(lead["website"])
                if normalized_website in existing_websites:
                    continue
                existing_websites.add(normalized_website)

            # Skip if phone already exists
            if lead.get("phone"):
                normalized_phone = self._normalize_phone(lead["phone"])
                if normalized_phone in existing_phones:
                    continue
                existing_phones.add(normalized_phone)

            # Skip if we've seen this company before in discovery
            if self.state_manager.is_company_seen(company_name):
                continue

            # Skip if previously filtered out
            if self.state_manager.is_company_filtered(company_name):
                continue

            # Calculate ICP score
            icp_score = self.calculate_icp_score(lead)
            lead["icp_score"] = icp_score

            # Filter by ICP threshold
            if icp_score < self.icp.min_score_threshold:
                self.state_manager.mark_company_filtered(company_name)
                continue

            # Mark as seen
            self.state_manager.mark_company_seen(company_name)

            # Add to filtered list
            filtered_leads.append(lead)
            existing_names.add(normalized_name)

        # Sort by ICP score (highest first)
        filtered_leads.sort(key=lambda x: x.get("icp_score", 0), reverse=True)

        # Limit to daily capacity
        remaining_capacity = self.get_remaining_daily_capacity()
        return filtered_leads[:remaining_capacity]

    def _normalize_company_name(self, name: str) -> str:
        """Normalize company name for deduplication"""
        name = name.lower().strip()
        # Remove common suffixes
        for suffix in ["inc", "llc", "ltd", "corp", "corporation", "company", "co", "inc.", "llc.", "ltd."]:
            name = name.replace(f" {suffix}", "").replace(f".{suffix}", "")
        return name.strip()

    def _normalize_website(self, website: str) -> str:
        """Normalize website URL for deduplication"""
        website = website.lower().strip().rstrip("/")
        website = website.replace("https://", "").replace("http://", "")
        website = website.replace("www.", "")
        return website

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number for deduplication"""
        # Extract digits only
        digits = "".join(c for c in phone if c.isdigit())
        # Keep last 10 digits (US format)
        return digits[-10:] if len(digits) >= 10 else digits

    def mark_leads_added(self, count: int):
        """Mark leads as added (increment daily counter)"""
        self.state_manager.increment_daily_leads(count)

    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get overall discovery statistics"""
        daily_stats = self.state_manager.get_daily_stats()
        cache_stats = self.api_cache.stats()

        return {
            "today": {
                "leads_added": daily_stats.get("leads_added", 0),
                "remaining_capacity": self.get_remaining_daily_capacity(),
                "daily_limit": self.daily_limit,
                "api_calls": daily_stats.get("api_calls", 0),
            },
            "cache": cache_stats,
            "state": {
                "companies_seen": len(self.state_manager.state.get("seen_companies", [])),
                "companies_filtered": len(self.state_manager.state.get("filtered_companies", [])),
                "sources_checked": len(self.state_manager.state.get("sources_checked", {})),
            }
        }


# Global instance (singleton pattern)
_discovery_manager_instance: Optional[SmartLeadDiscoveryManager] = None


def get_discovery_manager(
    daily_limit: Optional[int] = None,
    api_cache_ttl_hours: int = 24,
) -> SmartLeadDiscoveryManager:
    """Get or create the global discovery manager instance"""
    global _discovery_manager_instance

    if _discovery_manager_instance is None:
        # Get daily limit from environment or use default
        import os
        limit = daily_limit or int(os.getenv("DAILY_LEAD_LIMIT", "50"))

        _discovery_manager_instance = SmartLeadDiscoveryManager(
            daily_limit=limit,
            api_cache_ttl_hours=api_cache_ttl_hours,
        )

    return _discovery_manager_instance
