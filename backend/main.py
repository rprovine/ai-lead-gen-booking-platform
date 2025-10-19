from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json

# LangChain imports
from langchain_anthropic import ChatAnthropic
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.documents import Document

# Database and API imports
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("Firebase not available - using in-memory storage")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field
import httpx
from bs4 import BeautifulSoup

# Real lead scraping imports
from lead_scrapers import RealLeadDiscoveryOrchestrator

# PDF generation imports
from sales_playbook_generator import SalesPlaybookPDFGenerator
from fastapi.responses import Response

# Communication imports - make optional
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

try:
    from hubspot import HubSpot
    HUBSPOT_AVAILABLE = True
except ImportError:
    HUBSPOT_AVAILABLE = False

# Load environment variables
load_dotenv()

# Import database and scraper AFTER load_dotenv() so env vars are available
from database import db as supabase_db
from lenilani_scraper import lenilani_content
from perplexity_research import PerplexityResearcher
from executive_finder import ExecutiveContactFinder
from linkedin_sales_navigator import LinkedInSalesNavigator

# In-memory storage for demo purposes
in_memory_db = {
    'leads': [],
    'campaigns': [],
    'appointments': [],
    'outreach_log': []
}

# Initialize Firebase if available
db = None
if FIREBASE_AVAILABLE and os.path.exists(os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', '')):
    try:
        cred = credentials.Certificate(os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH'))
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase initialized successfully")
    except Exception as e:
        print(f"Firebase initialization failed: {e}, using in-memory storage")

# Initialize LLMs only if API keys are available
claude = None
embeddings = None

if os.getenv('ANTHROPIC_API_KEY') and os.getenv('ANTHROPIC_API_KEY') != 'your_key_here':
    try:
        claude = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
            temperature=0.3
        )
        print("Claude Sonnet 4.5 initialized successfully")
    except Exception as e:
        print(f"Claude initialization failed: {e}")

if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your_key_here':
    try:
        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
        print("OpenAI embeddings initialized successfully")
    except Exception as e:
        print(f"OpenAI initialization failed: {e}")

# Initialize communication clients
sendgrid_client = None
twilio_client = None
hubspot_client = None

if SENDGRID_AVAILABLE and os.getenv('SENDGRID_API_KEY', 'your_key_here') != 'your_key_here':
    try:
        sendgrid_client = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
    except Exception as e:
        print(f"SendGrid initialization failed: {e}")

if TWILIO_AVAILABLE and os.getenv('TWILIO_ACCOUNT_SID', 'your_sid_here') != 'your_sid_here':
    try:
        twilio_client = TwilioClient(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
    except Exception as e:
        print(f"Twilio initialization failed: {e}")

if HUBSPOT_AVAILABLE and os.getenv('HUBSPOT_API_KEY', 'your_key_here') != 'your_key_here':
    try:
        hubspot_client = HubSpot(access_token=os.getenv('HUBSPOT_API_KEY'))
    except Exception as e:
        print(f"HubSpot initialization failed: {e}")

# Create FastAPI app
app = FastAPI(title="LeniLani Lead Generation Platform")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://lenilani.com", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to load LeniLani content
@app.on_event("startup")
async def startup_event():
    """Load LeniLani content on startup"""
    await lenilani_content.load_content()
    print("✅ Startup complete - LeniLani content loaded")

# ============= MODELS =============
class Lead(BaseModel):
    id: Optional[str] = None
    company_name: str
    website: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    industry: str
    employee_count: Optional[int] = None
    location: str
    tech_stack: List[str] = []
    pain_points: List[str] = []
    score: float = 0.0
    status: str = "new"
    source: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class Campaign(BaseModel):
    name: str
    target_criteria: Dict
    message_template: str
    channels: List[str]  # email, sms, linkedin
    status: str = "draft"

class Appointment(BaseModel):
    lead_id: str
    date_time: str
    location: str = "1050 Queen Street, Suite 100, Honolulu, HI 96814"
    meeting_type: str = "in_person"  # in_person, virtual
    notes: str = ""

# ============= LEAD DISCOVERY =============
class LeadDiscoveryService:
    def __init__(self):
        try:
            self.search = DuckDuckGoSearchRun()
        except:
            self.search = None
            print("DuckDuckGo search not available")

        # Initialize real scraping orchestrator
        linkedin_api_key = os.getenv('LINKEDIN_API_KEY')
        serpapi_key = os.getenv('SERPAPI_KEY')
        self.real_scraper = RealLeadDiscoveryOrchestrator(
            linkedin_api_key=linkedin_api_key,
            serpapi_key=serpapi_key
        )
        self.use_real_data = os.getenv('USE_REAL_DATA', 'true').lower() == 'true'

        if self.use_real_data:
            print("🚀 Real lead discovery enabled - will scrape from LinkedIn, Google, Pacific Business News, and Hawaii directories")
        else:
            print("📋 Using demo mode - set USE_REAL_DATA=true in .env to enable real scraping")

    async def discover_hawaii_businesses(
        self,
        industry: Optional[str] = None,
        island: Optional[str] = None,
        business_type: Optional[str] = None,
        min_employees: Optional[int] = None,
        max_employees: Optional[int] = None,
        max_leads: int = 50
    ) -> List[Dict]:
        """
        Discover Hawaii businesses needing tech services with advanced filtering

        Args:
            industry: Filter by industry (e.g., 'tourism', 'healthcare', 'technology')
            island: Filter by Hawaiian island (e.g., 'Oahu', 'Maui', 'Kauai', 'Big Island', 'Molokai', 'Lanai')
            business_type: Filter by business type (e.g., 'hotel', 'restaurant', 'clinic')
            min_employees: Minimum employee count
            max_employees: Maximum employee count
            max_leads: Maximum number of leads to discover

        Returns:
            List of discovered business leads
        """

        if self.use_real_data:
            # Use real scraping from multiple sources
            print(f"🔍 Discovering real Hawaii businesses from multiple sources...")
            print(f"   - LinkedIn company search")
            print(f"   - Pacific Business News")
            print(f"   - Google Business/Maps")
            print(f"   - Yelp")
            print(f"   - Apple Maps")
            print(f"   - Better Business Bureau")
            print(f"   - TripAdvisor")
            print(f"   - Hawaii business directories (Chamber, HTDC, Hawaii Business Mag)")

            if island:
                print(f"   🏝️  Filtering by island: {island}")
            if industry:
                print(f"   🏢  Filtering by industry: {industry}")
            if business_type:
                print(f"   🏪  Filtering by business type: {business_type}")

            try:
                real_leads = await self.real_scraper.discover_leads(
                    industry=industry,
                    location="Hawaii",
                    island=island,
                    business_type=business_type,
                    min_employees=min_employees,
                    max_employees=max_employees,
                    max_leads=max_leads
                )

                # Enrich leads with default values if missing
                enriched_leads = []
                for lead in real_leads:
                    # Set defaults for missing fields
                    if 'employee_count' not in lead:
                        lead['employee_count'] = self._estimate_employee_count(lead)
                    if 'industry' not in lead:
                        lead['industry'] = industry or "Business Services"
                    if 'tech_stack' not in lead:
                        lead['tech_stack'] = ["Unknown"]
                    if 'pain_points' not in lead or lead['pain_points'] == ["Needs digital transformation"]:
                        # Generate AI-powered, industry-specific pain points
                        lead['pain_points'] = self._generate_pain_points(lead)
                    if 'status' not in lead:
                        lead['status'] = "new"
                    if 'location' not in lead:
                        lead['location'] = "Hawaii"

                    enriched_leads.append(lead)

                print(f"✓ Successfully discovered {len(enriched_leads)} real leads")
                return enriched_leads

            except Exception as e:
                print(f"❌ Error in real lead discovery: {e}")
                print(f"   No demo data available - please check your API keys and try again")
                return []
        else:
            print("⚠️ USE_REAL_DATA is set to false. Set USE_REAL_DATA=true in .env to discover real businesses")
            return []

    def _estimate_employee_count(self, lead: Dict) -> int:
        """Estimate employee count based on available data"""
        # Use business signals to estimate size
        if lead.get('reviews', 0) > 100:
            return 100
        elif lead.get('reviews', 0) > 50:
            return 50
        elif lead.get('rating', 0) > 4.5:
            return 30
        else:
            return 15

    def _generate_pain_points(self, lead: Dict) -> List[str]:
        """
        Generate AI-powered, industry-specific pain points for a lead

        Args:
            lead: Lead data dictionary with company_name, industry, etc.

        Returns:
            List of 2-4 specific pain points relevant to this company
        """
        try:
            company_name = lead.get('company_name', 'Unknown Company')
            industry = lead.get('industry', 'Business Services')
            employee_count = lead.get('employee_count', 15)
            location = lead.get('location', 'Hawaii')
            description = lead.get('description', '')

            # Create a focused prompt for pain point generation
            prompt = f"""Generate 3-4 specific, realistic business pain points for this Hawaii company:

Company: {company_name}
Industry: {industry}
Size: {employee_count} employees
Location: {location}
Description: {description}

Requirements:
1. Pain points must be SPECIFIC to this industry and company size
2. Consider Hawaii-specific challenges (tourism seasonality, island logistics, local market)
3. Focus on technology, operations, marketing, or customer service challenges
4. Be realistic and actionable (not generic like "needs digital transformation")
5. Each pain point should be 3-8 words

Return ONLY a JSON array of 3-4 pain point strings, nothing else.
Example format: ["Specific challenge 1", "Specific challenge 2", "Specific challenge 3"]"""

            if claude:
                result = claude.invoke(prompt)

                # Extract JSON array from response
                import json
                import re

                # Try to find JSON array in response
                json_match = re.search(r'\[[\s\S]*?\]', result.content)
                if json_match:
                    pain_points = json.loads(json_match.group(0))
                    if isinstance(pain_points, list) and len(pain_points) >= 2:
                        # Return 2-4 pain points
                        return pain_points[:4]

        except Exception as e:
            print(f"⚠️ Error generating pain points for {lead.get('company_name')}: {e}")

        # Fallback: industry-specific default pain points
        industry_defaults = {
            "Tourism & Hospitality": [
                "Seasonal booking fluctuations",
                "Manual reservation management",
                "Limited guest communication automation"
            ],
            "Healthcare": [
                "Manual appointment scheduling",
                "Paper-based patient records",
                "Limited telehealth capabilities"
            ],
            "Retail": [
                "Inventory tracking inefficiencies",
                "Limited e-commerce presence",
                "No customer analytics"
            ],
            "Food & Beverage": [
                "Manual ordering processes",
                "No online ordering system",
                "Limited delivery integration"
            ],
            "Real Estate": [
                "Manual property listings",
                "No virtual tour capabilities",
                "Limited CRM integration"
            ],
            "Professional Services": [
                "Manual client onboarding",
                "Limited digital marketing",
                "No automated scheduling"
            ]
        }

        # Return industry-specific defaults or generic ones
        industry = lead.get('industry', 'Business Services')
        for key in industry_defaults:
            if key.lower() in industry.lower():
                return industry_defaults[key]

        # Final fallback
        return [
            "Limited digital presence",
            "Manual business processes",
            "No customer analytics"
        ]

    def _get_demo_businesses(self) -> List[Dict]:
        """Return sample Hawaii businesses for demo purposes with diverse profiles"""
        sample_businesses = [
            {
                "company_name": "Waikiki Grand Hotel & Spa",
                "website": "https://waikikigrand.example.com",
                "contact_email": "reservations@waikikigrand.example.com",
                "phone": "(808) 555-0123",
                "industry": "Tourism & Hospitality",
                "employee_count": 385,
                "location": "Waikiki, Honolulu, HI",
                "description": "450-room beachfront resort with spa, 3 restaurants, and conference facilities. Catering to international tourists and business travelers.",
                "tech_stack": ["Opera PMS", "WordPress", "Mailchimp"],
                "pain_points": ["Guest messaging requires manual SMS", "Concierge overwhelmed with repetitive questions", "No AI for booking modifications"],
                "score": 92.0,
                "status": "new",
                "source": "demo_data",
                "recent_news": "Recently announced $12M renovation project. Expanding conference center to attract more corporate events. Seeking technology partners for digital transformation initiative."
            },
            {
                "company_name": "Maui Medical Associates",
                "website": "https://mauimedical.example.com",
                "contact_email": "admin@mauimedical.example.com",
                "phone": "(808) 555-0245",
                "industry": "Healthcare",
                "employee_count": 67,
                "location": "Kahului, Maui, HI",
                "description": "Multi-specialty medical practice serving 15,000+ patients across Maui County. Specializes in family medicine, pediatrics, and geriatric care.",
                "tech_stack": ["Epic EHR", "Basic website", "Phone system"],
                "pain_points": ["Phone lines overwhelmed with appointment calls", "No online scheduling system", "Patients missing follow-up appointments"],
                "score": 88.0,
                "status": "new",
                "source": "demo_data",
                "recent_news": "Received $2.3M federal grant for telehealth expansion. Actively hiring 5 new physicians. Looking to modernize patient communication systems."
            },
            {
                "company_name": "Kona Coffee Cooperative",
                "website": "https://konacoffee.example.com",
                "contact_email": "sales@konacoffee.example.com",
                "phone": "(808) 555-0389",
                "industry": "Agriculture & Food",
                "employee_count": 143,
                "location": "Captain Cook, Big Island, HI",
                "description": "100% Kona coffee grower cooperative representing 85 small family farms. Sells premium coffee direct-to-consumer and wholesale.",
                "tech_stack": ["Shopify", "QuickBooks", "Excel for inventory"],
                "pain_points": ["No inventory forecasting", "Manual order processing", "Limited customer data analytics"],
                "score": 75.0,
                "status": "new",
                "source": "demo_data",
                "recent_news": "Export orders to Japan increased 340% this year. Struggling to keep up with demand. Voted 'Best Kona Coffee' by Hawaii Magazine 2025."
            },
            {
                "company_name": "Pacific Legal Group",
                "website": "https://pacificlegalhi.example.com",
                "contact_email": "intake@pacificlegalhi.example.com",
                "phone": "(808) 555-0512",
                "industry": "Professional Services",
                "employee_count": 28,
                "location": "Downtown Honolulu, HI",
                "description": "Full-service law firm specializing in real estate, business law, and estate planning. Serves both individuals and corporations.",
                "tech_stack": ["Clio", "WordPress", "DocuSign"],
                "pain_points": ["Client intake forms still paper-based", "No AI for document review", "Marketing relies solely on referrals"],
                "score": 81.0,
                "status": "new",
                "source": "demo_data",
                "recent_news": "Named to Hawaii Business Magazine's Top 50 law firms. Opened second office in Kapolei. Senior partner retiring, firm transitioning to next generation leadership."
            },
            {
                "company_name": "North Shore Surf School",
                "website": "https://northshoresurf.example.com",
                "contact_email": "book@northshoresurf.example.com",
                "phone": "(808) 555-0678",
                "industry": "Tourism & Recreation",
                "employee_count": 24,
                "location": "Haleiwa, Oahu, HI",
                "description": "Premier surf instruction school on Oahu's famous North Shore. Offers group lessons, private coaching, and surf camps.",
                "tech_stack": ["WordPress", "Square", "Google Calendar"],
                "pain_points": ["Double-bookings happen frequently", "No automated reminder system", "Weather cancellations require manual calls"],
                "score": 77.0,
                "status": "new",
                "source": "demo_data",
                "recent_news": "Featured on Netflix surf documentary. Bookings up 215% but struggling with operations. Expanding to offer SUP and hydrofoil lessons."
            },
            {
                "company_name": "Honolulu Construction & Development",
                "website": "https://honoluluconstruction.example.com",
                "contact_email": "bids@honoluluconstruction.example.com",
                "phone": "(808) 555-0891",
                "industry": "Construction & Real Estate",
                "employee_count": 156,
                "location": "Kakaako, Honolulu, HI",
                "description": "Commercial construction firm specializing in high-rise condos and mixed-use developments. Active on 12 current projects.",
                "tech_stack": ["Procore", "AutoCAD", "Excel", "Email"],
                "pain_points": ["Project data scattered across platforms", "No centralized client portal", "Bid proposals take weeks to prepare"],
                "score": 86.0,
                "status": "new",
                "source": "demo_data",
                "recent_news": "Won $87M contract for new Kakaako residential tower. Hiring 40 new employees. Investing in technology to improve project management efficiency."
            },
            {
                "company_name": "Island Fresh Poke Co.",
                "website": "https://islandfreshpoke.example.com",
                "contact_email": "catering@islandfreshpoke.example.com",
                "phone": "(808) 555-1024",
                "industry": "Food & Beverage",
                "employee_count": 52,
                "location": "Kailua, Oahu, HI",
                "description": "Local poke chain with 6 locations across Oahu. Known for sustainable fishing practices and farm-fresh ingredients.",
                "tech_stack": ["Toast POS", "Basic website", "Instagram"],
                "pain_points": ["No online ordering system", "Catering bookings via phone/text only", "No customer loyalty program"],
                "score": 71.0,
                "status": "new",
                "source": "demo_data",
                "recent_news": "Opening 3 new locations on neighbor islands. Featured in Food & Wine's 'Best Poke in America'. Seeking technology to scale operations efficiently."
            },
            {
                "company_name": "Big Island Adventure Helicopters",
                "website": "https://bigislandchoppers.example.com",
                "contact_email": "tours@bigislandchoppers.example.com",
                "phone": "(808) 555-1247",
                "industry": "Tourism & Aviation",
                "employee_count": 34,
                "location": "Hilo, Big Island, HI",
                "description": "Helicopter tour company offering volcano tours, waterfall adventures, and custom aerial photography.",
                "tech_stack": ["Peek Pro", "WordPress", "Weather API"],
                "pain_points": ["Last-minute weather cancellations create chaos", "Can't predict seasonal demand patterns", "No automated rebooking system"],
                "score": 84.0,
                "status": "new",
                "source": "demo_data",
                "recent_news": "Added 2 new helicopters to fleet ($4.2M investment). Kilauea activity increasing tourism demand 400%. Need better forecasting tools to optimize scheduling."
            },
            {
                "company_name": "Kauai Renewable Energy Solutions",
                "website": "https://kauaisolar.example.com",
                "contact_email": "info@kauaisolar.example.com",
                "phone": "(808) 555-1456",
                "industry": "Energy & Sustainability",
                "employee_count": 41,
                "location": "Lihue, Kauai, HI",
                "description": "Solar installation and energy consulting firm. Services residential and commercial properties across Kauai.",
                "tech_stack": ["Salesforce", "Google Workspace", "CAD software"],
                "pain_points": ["Lead qualification takes too long", "No ROI calculator for customers", "Proposal generation is manual"],
                "score": 79.0,
                "status": "new",
                "source": "demo_data",
                "recent_news": "New state solar incentives boosted leads 500%. Backlog of 200+ consultation requests. Recently won 'Green Business of the Year' award."
            },
            {
                "company_name": "Aloha Wellness & Rehabilitation",
                "website": "https://alohawellness.example.com",
                "contact_email": "appointments@alohawellness.example.com",
                "phone": "(808) 555-1678",
                "industry": "Healthcare & Wellness",
                "employee_count": 73,
                "location": "Pearl City, Oahu, HI",
                "description": "Integrated wellness center offering physical therapy, chiropractic care, acupuncture, and massage therapy.",
                "tech_stack": ["Mindbody", "Basic website", "Paper intake forms"],
                "pain_points": ["Patients miss appointments (20% no-show rate)", "No automated follow-up sequences", "Referral tracking is manual"],
                "score": 74.0,
                "status": "new",
                "source": "demo_data",
                "recent_news": "Expanding to second location in Kapolei. Added sports medicine program for UH athletes. Looking for technology to reduce no-shows and improve patient outcomes."
            }
        ]
        return sample_businesses

    async def analyze_website(self, url: str) -> Dict:
        """Analyze a company website for opportunities"""
        analysis = {
            "tech_stack": ["WordPress", "Google Analytics"],
            "digital_maturity": 5,
            "pain_points": [
                "Outdated design",
                "No live chat support",
                "Limited mobile optimization",
                "No AI/chatbot integration"
            ],
            "recommended_services": [
                "AI Chatbot Development",
                "Website Modernization",
                "Data Analytics Dashboard",
                "Digital Marketing Optimization"
            ],
            "estimated_budget": "$15,000 - $30,000",
            "priority_level": "High"
        }

        if claude:
            try:
                loader = WebBaseLoader(url)
                documents = loader.load()

                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )
                chunks = text_splitter.split_documents(documents)

                analysis_prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are analyzing a company website to identify technology consulting opportunities for LeniLani Consulting. We offer: AI/Chatbot development, Data Analytics, Fractional CTO services, Digital Marketing/HubSpot."),
                    ("human", "Analyze this website content and identify: 1) Current tech stack, 2) Digital maturity level (1-10), 3) Potential pain points, 4) Services they might need from us, 5) Estimated budget range. Website content: {content}")
                ])

                chain = analysis_prompt | claude
                ai_analysis = chain.invoke({"content": str(chunks[:5])})
                analysis["ai_insights"] = ai_analysis.content
            except Exception as e:
                print(f"Error analyzing website with AI: {e}")

        return analysis

# ============= LEAD SCORING & QUALIFICATION =============
class LeadScoringAgent:
    def __init__(self):
        self.scoring_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a lead scoring expert for LeniLani Consulting. Score leads based on:
            - Company size (larger = higher score)
            - Technology adoption level (lower = higher opportunity)
            - Industry fit (tourism, healthcare, finance, government = high)
            - Location (Oahu = highest, neighbor islands = medium)
            - Pain points matching our services
            - Budget indicators

            Return a JSON with score (0-100) and explanation."""),
            ("human", "Score this lead: {lead_data}")
        ])

    async def score_lead(self, lead: Lead) -> Dict:
        base_score = 50.0
        explanation = []

        # Industry scoring
        high_value_industries = ["tourism", "hospitality", "healthcare", "finance", "government"]
        if any(ind in lead.industry.lower() for ind in high_value_industries):
            base_score += 15
            explanation.append("High-value industry match")

        # Location scoring
        if "honolulu" in lead.location.lower() or "oahu" in lead.location.lower():
            base_score += 10
            explanation.append("Prime Oahu location")
        elif "hawaii" in lead.location.lower():
            base_score += 5
            explanation.append("Hawaii location")

        # Company size scoring
        if lead.employee_count:
            if lead.employee_count > 100:
                base_score += 15
                explanation.append("Large company (100+ employees)")
            elif lead.employee_count > 50:
                base_score += 10
                explanation.append("Medium company (50-100 employees)")

        # Pain points scoring
        if len(lead.pain_points) >= 3:
            base_score += 10
            explanation.append(f"Multiple pain points identified ({len(lead.pain_points)})")

        # Try to get AI-enhanced score with Claude
        if claude:
            try:
                chain = self.scoring_prompt | claude
                result = chain.invoke({"lead_data": lead.dict()})

                # Try to extract score from AI response
                import json
                import re

                # Try to find JSON in response
                json_match = re.search(r'\{[\s\S]*\}', result.content)
                if json_match:
                    try:
                        ai_result = json.loads(json_match.group(0))
                        if 'score' in ai_result:
                            ai_score = float(ai_result['score'])
                            # Use weighted average: 60% AI, 40% rule-based
                            final_score = (ai_score * 0.6) + (base_score * 0.4)
                            if 'explanation' in ai_result:
                                explanation = ai_result['explanation'] if isinstance(ai_result['explanation'], list) else [ai_result['explanation']]
                            print(f"✓ AI scored lead: {ai_score} (base: {base_score}, final: {final_score:.1f})")
                            return {
                                "score": round(min(100, final_score)),
                                "explanation": explanation
                            }
                    except:
                        pass
            except Exception as e:
                print(f"Error scoring with AI: {e}")

        # Fallback to rule-based score
        return {
            "score": round(min(100, base_score)),
            "explanation": explanation
        }

# ============= PERSONALIZED OUTREACH =============
class OutreachGenerator:
    def __init__(self):
        self.email_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are creating personalized outreach for LeniLani Consulting.
            We're based in Honolulu (1050 Queen Street, Suite 100) and offer AI/ML consulting,
            custom chatbots, data analytics, fractional CTO services, and digital marketing.

            Create compelling, personalized messages that:
            1. Reference specific company pain points
            2. Offer concrete value propositions
            3. Include relevant case studies
            4. Have a clear call-to-action for an in-person meeting
            5. Use a professional but friendly Hawaii business tone

            Keep emails under 200 words."""),
            ("human", "Create outreach email for: {lead_data}")
        ])

    async def generate_email(self, lead: Lead) -> str:
        # Default template
        email = f"""Aloha from LeniLani Consulting,

I noticed {lead.company_name} is doing great work in Hawaii's {lead.industry} sector.

Based on my research, I see opportunities where we could help:
{chr(10).join(f'• {pain}' for pain in lead.pain_points[:3])}

At LeniLani, we specialize in AI/chatbot solutions, data analytics, and digital transformation for Hawaii businesses. We've helped companies similar to yours increase efficiency by 40% and reduce operational costs significantly.

I'd love to meet in person at our Honolulu office (1050 Queen Street, Suite 100) to discuss how we can support {lead.company_name}'s growth.

Would next week work for a 30-minute consultation?

Mahalo,
The LeniLani Team
808-XXX-XXXX
"""

        if claude:
            try:
                chain = self.email_prompt | claude
                ai_email = chain.invoke({"lead_data": lead.dict()})
                email = ai_email.content
            except Exception as e:
                print(f"Error generating email with AI: {e}")

        return email

    async def generate_sms(self, lead: Lead) -> str:
        sms = f"Aloha from LeniLani Consulting! We help Hawaii businesses with AI & digital transformation. Interested in a free consultation at our Honolulu office? Reply YES"

        return sms

    async def generate_linkedin_message(self, lead: Lead) -> str:
        message = f"""Aloha! I see you're with {lead.company_name}. We at LeniLani Consulting specialize in helping Hawaii {lead.industry} companies leverage AI and analytics. Would love to connect and explore potential synergies. Based in Honolulu - happy to meet in person!"""

        return message

# ============= AI SALES INTELLIGENCE =============
class SalesIntelligenceAnalyzer:
    """
    Comprehensive AI-powered sales analysis for each lead
    Provides actionable insights, hot buttons, and sales strategies
    """

    def __init__(self):
        # Initialize Perplexity AI researcher for real-time company intelligence
        self.perplexity = PerplexityResearcher()

        # Initialize executive contact finder
        self.executive_finder = ExecutiveContactFinder()

        # Initialize LinkedIn Sales Navigator
        self.linkedin_nav = LinkedInSalesNavigator()

        # Get LeniLani content for context
        lenilani_context = lenilani_content.get_context_string() if lenilani_content.content.get('loaded') else """
LeniLani Consulting Company Information:

ABOUT US:
Hawaii-based AI and software development consultancy located at 1050 Queen Street, Suite 100, Honolulu, HI 96814

OUR SERVICES:
- AI Chatbot Development & Integration
- Data Analytics & BI Dashboards
- Fractional CTO Services
- HubSpot/Digital Marketing Automation
- Custom Software Development
- ML/AI Model Development

VALUE PROPOSITIONS:
- Local Hawaii presence with in-person collaboration
- Proven ROI: 40%+ efficiency gains for clients
- Industry expertise in Tourism, Healthcare, and Technology
- Rapid deployment: Production-ready in weeks, not months
"""

        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are an expert B2B sales strategist for LeniLani Consulting.

{lenilani_context}

Analyze this lead and provide HIGHLY SPECIFIC, DETAILED, UNIQUE sales intelligence for THIS SPECIFIC COMPANY.
Use the LeniLani company information above to reference our ACTUAL services, value propositions, and proven results.

CRITICAL: Each section must explain WHY it matters for THIS company. Be creative and vary your recommendations.

IMPORTANT JSON RULES:
- Return ONLY valid JSON - no commentary before or after
- All strings must use double quotes, never single quotes
- No trailing commas after last item in arrays or objects
- Ensure ALL array items have commas between them
- Check carefully for missing commas between object properties

Return ONLY valid JSON with this exact structure (use formatted strings to include WHY explanations):
{{{{"executive_summary": "Detailed 3-4 sentence analysis. Reference their specific situation, recent developments, why NOW is the right time, estimated deal size, and unique strategic approach for THIS company.", "key_executives": ["Name | Title | Why target them: explanation"], "recent_developments": ["Development/trend | Why it matters: impact on this company"], "hot_buttons": ["Pain point | Why urgent: timing/reason | Our solution: specific fix"], "recommended_approach": "Multi-paragraph strategy explaining: 1) Why THIS approach for THIS company, 2) What makes them different, 3) Specific tactics unique to their situation", "talking_points": ["Value proposition | Why THIS company cares: reason | Proof: metric/example"], "decision_maker": "Target role (with name if known) | Why them: reasoning | Priorities: list | Best contact: method, timing, and reasoning", "budget": "Range: $X-$Y | Likelihood: High/Medium/Low | Why: detailed signals and justification specific to this company", "competitive_positioning": "Likely competitors: list with threats | Our differentiators: list with why each matters to THIS company | Hawaii advantage: specific local benefits for them", "appointment_strategy": "Hook: specific offer | Why this hook works for THIS company: reasoning | Format: in-person/virtual with reasoning | Follow-up: timeline with reasoning", "next_steps": ["Action | Why: reason for this company | When: timing"]}}}}"""),
            ("human", """Analyze this Hawaii business lead with ALL available information:

Company: {company_name}
Industry: {industry}
Location: {location}
Size: {employee_count} employees
Website: {website}
Current Pain Points: {pain_points}
Lead Score: {score}/100

{executives_info}

{recent_insights}

Provide detailed, company-specific sales intelligence. Make it UNIQUE to this company. Explain WHY for every recommendation. Return valid JSON ONLY.""")
        ])

    async def analyze_lead_for_sales(self, lead_data: Dict) -> Dict:
        """Generate comprehensive AI sales intelligence"""

        # First, enrich lead with additional research
        enriched_data = await self._enrich_lead_data(lead_data)

        # Try to get AI-powered insights first with enriched data
        analysis = None
        if claude:
            try:
                analysis = await self._get_ai_insights(enriched_data)
                print(f"✓ Generated AI insights for {enriched_data.get('company_name')}")
            except Exception as e:
                print(f"AI enhancement error: {e}")

        # Fallback to structured template if AI fails
        if not analysis:
            employee_count = lead_data.get('employee_count', 0)
            score = lead_data.get('score', 0)
            industry = lead_data.get('industry', 'business')
            company_name = lead_data.get('company_name', 'Unknown')
            location = lead_data.get('location', 'Hawaii')

            # Create more detailed, specific executive summary
            size_desc = "small" if employee_count < 50 else ("mid-sized" if employee_count < 200 else "large")
            score_desc = "high-potential" if score >= 75 else ("qualified" if score >= 60 else "emerging")

            # Build formatted strings with WHY explanations
            target_role = "CEO/Owner" if employee_count < 100 else ("COO/VP Operations" if industry in ["Tourism & Hospitality", "Retail"] else "CTO/Director of IT")

            analysis = {
                "executive_summary": f"{company_name} is a {size_desc} {industry} company ({employee_count} employees) based in {location} with a {score}/100 lead score, indicating a {score_desc} opportunity. As a Hawaii-based business, they would benefit from LeniLani's local AI/ML expertise and in-person collaboration. Estimated deal value: ${15000 if score < 75 else 45000}. Strategic approach: Lead with industry-specific AI solutions, emphasize local presence and Hawaii market expertise.",

                "key_executives": [
                    f"{target_role} | Why target them: Primary decision-maker for technology investments in {industry} companies of this size"
                ],

                "recent_developments": [
                    f"Hawaii {industry} sector facing increased competition from mainland companies | Why it matters: Need to modernize quickly to compete",
                    f"Rising labor costs in Hawaii making automation more attractive | Why it matters: ROI on AI solutions is now 40% faster than 2 years ago"
                ],

                "hot_buttons": [
                    f"Digital transformation lagging in Hawaii {industry} sector | Why urgent: Competitors gaining market share with modern tools | Our solution: Turnkey AI automation platform with Hawaii-specific customization",
                    f"Manual processes consuming {20 if employee_count < 100 else 40}+ hours/week | Why urgent: Labor costs 30% higher in Hawaii than mainland | Our solution: AI chatbot and workflow automation reduces manual work by 60%",
                    f"Difficulty attracting tech talent in Hawaii | Why urgent: Can't build in-house team cost-effectively | Our solution: Fractional CTO + managed AI services - no hiring needed",
                    f"Customer expectations for digital experience rising | Why urgent: {industry} customers expect mainland-level digital service | Our solution: Modern AI-powered customer engagement platform",
                    f"High Hawaii operating costs squeezing margins | Why urgent: Need efficiency gains to maintain profitability | Our solution: AI automation typically reduces costs $50K-$150K annually"
                ],

                "recommended_approach": f"Lead with quick-win AI chatbot demo specific to {industry} use cases. Emphasize we're local (1050 Queen Street), understand Hawaii business culture, and offer in-person collaboration. Position as long-term technology partner, not just vendor. Offer free AI readiness assessment to build trust. Follow up with case study from similar Hawaii {industry} client showing 40%+ efficiency gains.",

                "talking_points": [
                    f"40%+ efficiency gains for Hawaii {industry} businesses | Why THIS company cares: Same cost pressures, local market dynamics | Proof: 3 Hawaii {industry} case studies with documented ROI",
                    f"Only full-service AI/ML consultancy with physical Honolulu office | Why THIS company cares: Need local partner who understands Hawaii, not mainland remote team | Proof: 15+ successful Hawaii deployments",
                    f"Understand Hawaii {industry} challenges (shipping, island time, seasonality) | Why THIS company cares: Generic solutions don't work in Hawaii | Proof: Custom Hawaii-specific features in all our platforms",
                    f"Fractional CTO at ${employee_count * 200}/month | Why THIS company cares: Can't afford full-time CTO but need strategic tech leadership | Proof: Average client saves $120K/year vs hiring",
                    f"60-90 day implementation for {industry} | Why THIS company cares: Need fast results, not 6-month projects | Proof: 85% of clients see ROI in first quarter",
                    f"All-in-one platform (AI + data + automation + CTO) | Why THIS company cares: Tired of managing multiple vendors | Proof: Clients reduce vendor count by average of 4"
                ],

                "decision_maker": f"{target_role} | Why them: Controls technology budget and feels pain of manual processes daily | Priorities: Revenue growth, cost reduction, modern customer experience | Best contact: Email first (9-11am HST) with {industry}-specific case study, LinkedIn connect 2 days later, phone follow-up on day 5. Avoid Friday afternoons.",

                "budget": f"Range: ${15000 if score < 70 else 25000}-${30000 if score < 80 else 75000} | Likelihood: {"High" if score >= 75 else ("Medium" if score >= 60 else "Low")} | Why: Lead score {score}/100 indicates {"strong" if score >= 70 else "moderate"} fit. {employee_count} employees × ${industry} benchmarks + Hawaii premium suggest budget exists. Pain points (manual work, costs) create urgency. Hawaii {industry} businesses typically allocate {1 if employee_count < 100 else 2}-3% revenue to tech, putting them in this range.",

                "competitive_positioning": f"Likely competitors: Mainland {industry} SaaS vendors (threat: cheaper but don't understand Hawaii), Hawaii freelancers (threat: lower price point), internal DIY (threat: free but slow) | Our differentiators: Full-service AI/ML consultancy (matters: one vendor vs many) + Physical Hawaii office (matters: in-person support) + {industry} expertise (matters: we've done this 15+ times locally) + All-in-one platform (matters: reduces complexity) | Hawaii advantage: We're at 1050 Queen Street. We get island time, shipping delays, tourism seasonality, local business culture. We can meet in person in 20 minutes. When systems go down, we're here - not calling mainland support at midnight their time.",

                "appointment_strategy": f"Hook: Free AI Readiness Assessment ($2,500 value) for Hawaii {industry} - includes competitive analysis showing how 3 mainland competitors compare to your current setup | Why this hook works: {industry} companies are worried about falling behind but don't know where to start - this removes risk and provides immediate value | Format: {'In-person at 1050 Queen Street office' if 'honolulu' in location.lower() or 'oahu' in location.lower() else 'Virtual (Zoom) with option for Honolulu office visit'} - allows hands-on demo | Follow-up: Day 0 email with case study, Day 2 LinkedIn (build relationship), Day 5 call (discuss assessment), Day 8 AI demo video (show capability), Day 12 ROI calculator (close deal). This cadence respects island time while maintaining momentum.",

                "next_steps": [
                    f"Research {company_name}'s website and social media | Why: Find specific pain points to reference in outreach | When: Today - takes 15 minutes",
                    f"Prepare {industry} case study from similar Hawaii client | Why: Proof that solutions work for their specific industry locally | When: Before first contact",
                    f"Draft personalized email with their specific challenges | Why: Generic outreach fails - need to show we understand THEIR business | When: Within 24 hours",
                    f"LinkedIn connect with decision maker, engage with posts | Why: Build relationship before sales pitch | When: 2 days before email",
                    f"Create custom AI chatbot demo with {company_name} logo | Why: Seeing their brand on working system is powerful closer | When: Before meeting"
                ]
            }

        # Add metadata
        analysis['generated_at'] = datetime.now().isoformat()
        analysis['lead_id'] = lead_data.get('id', 'unknown')
        analysis['confidence'] = lead_data.get('score', 0)

        # Add Perplexity research if available
        if 'perplexity_research' in enriched_data:
            analysis['perplexity_research'] = enriched_data['perplexity_research']
        if 'research_summary' in enriched_data:
            analysis['research_summary'] = enriched_data['research_summary']

        # Add executive contact information if available
        if 'decision_makers' in enriched_data:
            analysis['decision_makers'] = enriched_data['decision_makers']
        if 'executives' in enriched_data:
            analysis['executives'] = enriched_data['executives']

        return analysis

    async def _enrich_lead_data(self, lead_data: Dict) -> Dict:
        """Enrich lead with executive info, recent news, and additional research using Perplexity AI"""
        enriched = lead_data.copy()

        company_name = lead_data.get('company_name', '')
        website = lead_data.get('website', '')
        industry = lead_data.get('industry', '')
        location = lead_data.get('location', 'Hawaii')

        # Use Perplexity AI for comprehensive real-time research (past 90 days)
        print(f"🔬 Researching {company_name} with Perplexity AI...")
        perplexity_research = await self.perplexity.research_company(
            company_name=company_name,
            industry=industry,
            location=location
        )

        # Extract structured data from Perplexity research
        news_items = []
        executives = []

        if perplexity_research.get('has_recent_data'):
            print(f"✓ Found recent data for {company_name}")

            # Extract recent news
            if perplexity_research.get('recent_news'):
                news_items.append(perplexity_research['recent_news'])

            # Extract business developments
            if perplexity_research.get('business_developments'):
                news_items.append(perplexity_research['business_developments'])

            # Store full research for reference
            enriched['perplexity_research'] = perplexity_research
            enriched['research_summary'] = perplexity_research.get('summary', '')

        # Discover website if missing (critical for executive contact finding)
        if not website or website == '':
            print(f"🌐 No website found - discovering website for {company_name}...")
            website = await self._discover_company_website(company_name, location)
            if website:
                print(f"✓ Discovered website: {website}")
                # Update lead data with discovered website
                lead_data['website'] = website
            else:
                print(f"⚠️  Could not discover website for {company_name}")

        # Find decision maker contact information
        print(f"👔 Finding decision makers for {company_name}...")
        decision_makers = await self.executive_finder.find_decision_makers(
            company_name=company_name,
            website=website,
            industry=industry,
            employee_count=lead_data.get('employee_count')
        )

        if decision_makers.get('executives'):
            print(f"✓ Found {len(decision_makers['executives'])} decision makers")
            enriched['decision_makers'] = decision_makers
            executives.extend(decision_makers['executives'])

        # Fallback to website scraping if Perplexity didn't find recent data
        if not news_items:
            try:
                import aiohttp
                from bs4 import BeautifulSoup

                # Try to scrape company website for executive info if available
                if website and website.startswith('http'):
                    async with aiohttp.ClientSession() as session:
                        async with session.get(website, timeout=aiohttp.ClientTimeout(total=5)) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')

                                # Look for executive/leadership section
                                text = soup.get_text().lower()
                                if 'ceo' in text or 'president' in text or 'executive' in text:
                                    # Try to extract executive names
                                    for keyword in ['ceo', 'president', 'founder', 'owner', 'executive director']:
                                        if keyword in text:
                                            # Simple extraction - find text around the keyword
                                            idx = text.find(keyword)
                                            if idx > 0:
                                                context = text[max(0, idx-50):idx+100]
                                                # Look for capitalized names
                                                words = context.split()
                                                for i, word in enumerate(words):
                                                    if word.capitalize() == word and len(word) > 2:
                                                        if i+1 < len(words) and words[i+1].capitalize() == words[i+1]:
                                                            name = f"{word} {words[i+1]}"
                                                            role = keyword.upper()
                                                            if name not in [e.get('name') for e in executives]:
                                                                executives.append({'name': name, 'title': role})

                                print(f"Found {len(executives)} executives for {company_name}")
            except Exception as e:
                print(f"Website scraping error for {company_name}: {e}")

            # Use AI to generate news based on company info
            if claude and company_name:
                try:
                    news_prompt = f"What are the likely recent developments, challenges, or opportunities for {company_name}, a {lead_data.get('industry', 'business')} company in {lead_data.get('location', 'Hawaii')}? List 2-3 specific, realistic possibilities based on current industry trends."
                    news_response = claude.invoke(news_prompt)
                    news_items = [news_response.content[:500]]  # Take first 500 chars
                    print(f"Generated industry insights for {company_name}")
                except:
                    pass

        # Add enriched data
        if executives:
            enriched['executives'] = executives
        if news_items:
            enriched['recent_insights'] = news_items

        return enriched

    async def _discover_company_website(self, company_name: str, location: str = None) -> Optional[str]:
        """
        Discover company website using Google search via SerpAPI

        Args:
            company_name: Name of the company
            location: Location to narrow down search (optional)

        Returns:
            Company website URL if found, None otherwise
        """
        try:
            import os
            import aiohttp
            import re

            serpapi_key = os.getenv('SERPAPI_KEY')
            if not serpapi_key:
                return None

            # Build search query
            query = f"{company_name}"
            if location:
                query += f" {location}"
            query += " official website"

            # Use SerpAPI to search Google
            url = "https://serpapi.com/search"
            params = {
                'q': query,
                'api_key': serpapi_key,
                'engine': 'google',
                'num': 5
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Extract website from organic results
                        organic_results = data.get('organic_results', [])
                        for result in organic_results:
                            link = result.get('link', '')

                            # Skip social media and directory sites
                            skip_domains = ['facebook.com', 'linkedin.com', 'yelp.com', 'yellowpages.com',
                                           'instagram.com', 'twitter.com', 'pinterest.com']
                            if any(domain in link.lower() for domain in skip_domains):
                                continue

                            # Extract clean domain
                            if link and link.startswith('http'):
                                # Extract domain from URL
                                match = re.match(r'https?://([^/]+)', link)
                                if match:
                                    domain = match.group(1)
                                    # Remove www.
                                    domain = re.sub(r'^www\.', '', domain)
                                    return f"https://{domain}"

        except Exception as e:
            print(f"Website discovery error: {e}")

        return None

    async def _get_ai_insights(self, lead_data: Dict) -> Dict:
        """Get AI-enhanced insights from Claude"""
        try:
            # Prepare executive info
            executives = lead_data.get('executives', [])
            executives_info = ""
            if executives:
                executives_info = "Known Executives:\n"
                for exec in executives:
                    executives_info += f"- {exec.get('name')}, {exec.get('title')}\n"
            else:
                executives_info = "Executives: Unknown - research needed"

            # Prepare recent insights
            recent_insights = lead_data.get('recent_insights', [])
            insights_info = ""
            if recent_insights:
                insights_info = "Recent Industry Insights/Likely Developments:\n"
                for insight in recent_insights:
                    insights_info += f"- {insight}\n"
            else:
                insights_info = "Recent News: No specific news found - use industry trends"

            chain = self.analysis_prompt | claude
            response = chain.invoke({
                "company_name": lead_data.get('company_name', 'Unknown'),
                "industry": lead_data.get('industry', 'Business'),
                "location": lead_data.get('location', 'Hawaii'),
                "employee_count": lead_data.get('employee_count', 0) or 0,
                "website": lead_data.get('website', 'Not available'),
                "pain_points": ', '.join(lead_data.get('pain_points', [])) or 'Not specified',
                "score": lead_data.get('score', 0) or 0,
                "executives_info": executives_info,
                "recent_insights": insights_info
            })

            # Try to extract JSON from AI response
            import json
            import re

            content = response.content

            # Try to find JSON in the response (sometimes Claude adds explanation before/after)
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                json_str = json_match.group(0)

                # Robust JSON fixing
                original_str = json_str

                # Fix 1: Remove trailing commas before closing braces/brackets
                json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

                # Fix 2: Remove comments (not valid in JSON)
                json_str = re.sub(r'//.*?\n', '', json_str)

                # Fix 3: Add missing commas between array items
                # This is tricky - look for patterns like }" {" or "]" [" without comma
                json_str = re.sub(r'\}(\s*)\{', r'},\1{', json_str)
                json_str = re.sub(r'\](\s*)\[', r'],\1[', json_str)

                # Fix 4: Add missing commas after object properties
                # Look for patterns like "value" "key": without comma
                json_str = re.sub(r'\"(\s*)\n(\s*)\"', r'",\1\n\2"', json_str)

                # Fix 5: Fix unescaped quotes in strings (aggressive but careful)
                # This is complex, so we'll try to detect obvious cases
                # Look for "text "text" text" and fix middle quotes
                def fix_inner_quotes(match):
                    text = match.group(1)
                    # Replace internal quotes with escaped quotes
                    fixed = text.replace('"', '\\"')
                    return f'"{fixed}"'

                # Fix 6: Remove any non-JSON content after the last }
                last_brace = json_str.rfind('}')
                if last_brace != -1:
                    json_str = json_str[:last_brace+1]

                try:
                    parsed = json.loads(json_str)
                    print(f"✓ Successfully parsed AI JSON response")
                    return parsed
                except json.JSONDecodeError as je:
                    print(f"JSON parse error after fixes: {je}")
                    print(f"Failed to parse: {json_str[:300]}...")

                    # Try one more aggressive fix: use demjson3 if available
                    try:
                        import demjson3
                        parsed = demjson3.decode(json_str)
                        print(f"✓ Parsed with demjson3 (lenient parser)")
                        return parsed
                    except:
                        pass

                    # Print more context around the error for debugging
                    if je.pos:
                        start = max(0, je.pos - 150)
                        end = min(len(json_str), je.pos + 150)
                        error_snippet = json_str[start:end]
                        print(f"Error context: ...{error_snippet}...")
                        print(f"Error at character {je.pos}: {je.msg}")

            # Fallback: return None to use template
            print(f"Could not extract valid JSON from Claude response")
            return None

        except Exception as e:
            print(f"AI insights error: {e}")
            return None

# ============= APPOINTMENT BOOKING =============
class AppointmentScheduler:
    def __init__(self):
        self.office_address = os.getenv('OFFICE_ADDRESS', '1050 Queen Street, Suite 100, Honolulu, HI 96814')

    async def find_available_slots(self) -> List[Dict]:
        """Find available meeting slots"""
        slots = []
        now = datetime.now()

        for i in range(1, 15):  # Next 14 days
            day = now + timedelta(days=i)
            if day.weekday() < 5:  # Weekdays only
                # Morning slots
                morning_slot = day.replace(hour=9, minute=0, second=0, microsecond=0)
                slots.append({
                    "datetime": morning_slot.isoformat(),
                    "display": morning_slot.strftime("%A, %B %d at 9:00 AM HST"),
                    "available": True
                })

                # Afternoon slots
                afternoon_slot = day.replace(hour=14, minute=0, second=0, microsecond=0)
                slots.append({
                    "datetime": afternoon_slot.isoformat(),
                    "display": afternoon_slot.strftime("%A, %B %d at 2:00 PM HST"),
                    "available": True
                })

        return slots

    async def book_appointment(self, lead_id: str, date_time: str) -> Appointment:
        """Book an appointment and send confirmations"""
        appointment = Appointment(
            lead_id=lead_id,
            date_time=date_time,
            location=self.office_address,
            meeting_type="in_person",
            notes="Initial consultation - AI & Digital Transformation"
        )

        # Save to storage
        appointment_dict = appointment.dict()
        appointment_dict['id'] = f"apt_{len(in_memory_db['appointments']) + 1}"

        if db:
            try:
                db.collection('appointments').add(appointment_dict)
            except Exception as e:
                print(f"Error saving to Firebase: {e}")
                in_memory_db['appointments'].append(appointment_dict)
        else:
            in_memory_db['appointments'].append(appointment_dict)

        return appointment

# ============= API ENDPOINTS =============
discovery_service = LeadDiscoveryService()
scoring_agent = LeadScoringAgent()
outreach_generator = OutreachGenerator()
sales_intelligence = SalesIntelligenceAnalyzer()
pdf_generator = SalesPlaybookPDFGenerator()
scheduler = AppointmentScheduler()

@app.get("/")
async def root():
    return {
        "message": "LeniLani Lead Generation Platform API",
        "status": "active",
        "version": "1.0.0",
        "services": {
            "claude": claude is not None,
            "perplexity": True,
            "firebase": db is not None,
            "sendgrid": sendgrid_client is not None,
            "twilio": twilio_client is not None,
            "hubspot": hubspot_client is not None
        }
    }

@app.post("/api/leads/discover")
async def discover_leads(
    background_tasks: BackgroundTasks,
    industry: Optional[str] = None,
    island: Optional[str] = None,
    business_type: Optional[str] = None,
    min_employees: Optional[int] = None,
    max_employees: Optional[int] = None,
    max_leads: int = 50
):
    """
    Discover new leads from various sources with advanced filtering

    Args:
        industry: Filter by industry (e.g., 'tourism', 'healthcare', 'technology')
        island: Filter by Hawaiian island (e.g., 'Oahu', 'Maui', 'Kauai', 'Big Island', 'Molokai', 'Lanai')
        business_type: Filter by business type (e.g., 'hotel', 'restaurant', 'clinic')
        min_employees: Minimum employee count
        max_employees: Maximum employee count
        max_leads: Maximum number of leads to discover
    """
    leads = await discovery_service.discover_hawaii_businesses(
        industry=industry,
        island=island,
        business_type=business_type,
        min_employees=min_employees,
        max_employees=max_employees,
        max_leads=max_leads
    )

    # Get existing leads from database to check for duplicates
    existing_leads = await supabase_db.get_leads(limit=1000)
    existing_companies = {
        lead.get('company_name', '').lower().strip()
        for lead in existing_leads
        if lead.get('company_name')
    }

    # Score and save leads (skip duplicates)
    saved_leads = []
    skipped_duplicates = 0

    for lead_data in leads:
        company_name = lead_data.get('company_name', '').lower().strip()

        # Skip if company already exists in database
        if company_name in existing_companies:
            skipped_duplicates += 1
            print(f"⏭️  Skipping duplicate: {lead_data.get('company_name')}")
            continue

        # Map scraper field names to Lead model field names
        # Scrapers return 'phone' but Lead model expects 'contact_phone'
        if 'phone' in lead_data and not lead_data.get('contact_phone'):
            lead_data['contact_phone'] = lead_data.pop('phone')

        # Try to extract email from website or other fields if available
        if 'email' in lead_data and not lead_data.get('contact_email'):
            lead_data['contact_email'] = lead_data.pop('email')

        lead = Lead(**lead_data)
        scoring_result = await scoring_agent.score_lead(lead)
        lead.score = scoring_result['score']
        lead_dict = lead.dict()

        # Generate unique ID if not present
        if not lead_dict.get('id'):
            import uuid
            lead_dict['id'] = f"lead_{uuid.uuid4().hex[:8]}"

        # Map Python model field names to Supabase schema column names
        supabase_lead_dict = lead_dict.copy()
        if 'contact_email' in supabase_lead_dict:
            supabase_lead_dict['email'] = supabase_lead_dict.pop('contact_email')
        if 'contact_phone' in supabase_lead_dict:
            supabase_lead_dict['phone'] = supabase_lead_dict.pop('contact_phone')
        # Remove fields not in Supabase schema
        if 'status' in supabase_lead_dict:
            del supabase_lead_dict['status']
        if 'tech_stack' in supabase_lead_dict:
            del supabase_lead_dict['tech_stack']

        # Save to Supabase
        saved_lead = await supabase_db.upsert_lead(supabase_lead_dict)

        # Fallback to in-memory if Supabase fails
        if not saved_lead:
            in_memory_db['leads'].append(lead_dict)
            saved_leads.append(lead_dict)
        else:
            saved_leads.append(saved_lead)
            existing_companies.add(company_name)  # Add to set to avoid duplicates in this batch

    print(f"✅ Saved {len(saved_leads)} new leads, skipped {skipped_duplicates} duplicates")

    return {
        "message": "Lead discovery completed",
        "total_discovered": len(leads),
        "new_leads_saved": len(saved_leads),
        "duplicates_skipped": skipped_duplicates,
        "leads": saved_leads
    }

@app.post("/api/leads/analyze")
async def analyze_lead(url: str):
    """Analyze a specific company website"""
    analysis = await discovery_service.analyze_website(url)
    return {"analysis": analysis}

@app.post("/api/leads/score")
async def score_lead(lead: Lead):
    """Score a lead"""
    scoring_result = await scoring_agent.score_lead(lead)
    lead.score = scoring_result['score']

    # Save to storage
    lead_dict = lead.dict()
    lead_dict['id'] = f"lead_{len(in_memory_db['leads']) + 1}"

    if db:
        try:
            db.collection('leads').add(lead_dict)
        except Exception as e:
            print(f"Error saving to Firebase: {e}")
            in_memory_db['leads'].append(lead_dict)
    else:
        in_memory_db['leads'].append(lead_dict)

    return {
        "score": scoring_result['score'],
        "explanation": scoring_result['explanation'],
        "lead": lead_dict
    }

@app.get("/api/leads")
async def get_leads(status: Optional[str] = None, min_score: Optional[float] = None):
    """Get all leads with filtering"""
    # Try Supabase first
    leads = await supabase_db.get_leads(limit=100)

    # Fallback to in-memory if Supabase is empty
    if not leads:
        leads = in_memory_db['leads']

    # Apply filters if specified
    if status:
        leads = [l for l in leads if l.get('status') == status]
    if min_score:
        leads = [l for l in leads if l.get('score', 0) >= min_score]

    return leads

@app.post("/api/leads/{lead_id}/intelligence")
async def get_lead_intelligence(lead_id: str, refresh: bool = False):
    """Get comprehensive AI sales intelligence for a specific lead"""
    # Check for cached intelligence first (unless refresh is requested)
    if not refresh:
        cached_intelligence = await supabase_db.get_intelligence(lead_id)

        if cached_intelligence:
            print(f"✓ Using cached intelligence for {lead_id}")
            return {
                "lead_id": lead_id,
                "intelligence": cached_intelligence,
                "cached": True
            }
    else:
        print(f"🔄 Refresh requested - regenerating intelligence for {lead_id}")

    # Find the lead
    lead_data = await supabase_db.get_lead_by_id(lead_id)

    if not lead_data:
        # Fallback to in-memory
        for lead in in_memory_db['leads']:
            if lead.get('id') == lead_id:
                lead_data = lead
                break

    if not lead_data:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Generate comprehensive sales intelligence
    intelligence = await sales_intelligence.analyze_lead_for_sales(lead_data)

    # Save intelligence to Supabase for caching
    await supabase_db.save_intelligence(lead_id, intelligence)
    print(f"✓ Saved intelligence for {lead_id} to database")

    return {
        "lead_id": lead_id,
        "intelligence": intelligence,
        "cached": False
    }

@app.get("/api/leads/{lead_id}/playbook")
async def download_sales_playbook(lead_id: str):
    """Download PDF sales playbook for a lead"""
    # Find the lead
    lead_data = await supabase_db.get_lead_by_id(lead_id)

    if not lead_data:
        # Fallback to in-memory
        for lead in in_memory_db['leads']:
            if lead.get('id') == lead_id:
                lead_data = lead
                break

    if not lead_data:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Try to get cached intelligence
    intelligence = await supabase_db.get_intelligence(lead_id)

    # If not cached, generate new intelligence
    if not intelligence:
        intelligence = await sales_intelligence.analyze_lead_for_sales(lead_data)
        await supabase_db.save_intelligence(lead_id, intelligence)

    # Generate PDF
    pdf_bytes = pdf_generator.generate_playbook(lead_data, intelligence)

    # Return PDF
    filename = f"Sales_Playbook_{lead_data.get('company_name', 'Lead').replace(' ', '_')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@app.post("/api/leads/{lead_id}/email-template")
async def generate_email_template(lead_id: str, template_style: str = "professional"):
    """Generate email template populated with intelligence data"""
    # Find the lead
    lead_data = await supabase_db.get_lead_by_id(lead_id)

    if not lead_data:
        # Fallback to in-memory
        for lead in in_memory_db['leads']:
            if lead.get('id') == lead_id:
                lead_data = lead
                break

    if not lead_data:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Generate intelligence
    intelligence = await sales_intelligence.analyze_lead_for_sales(lead_data)

    # Generate email based on template style
    email_templates = {
        "professional": _generate_professional_email,
        "casual": _generate_casual_email,
        "consultative": _generate_consultative_email
    }

    template_func = email_templates.get(template_style, _generate_professional_email)
    email_content = template_func(lead_data, intelligence)

    # Extract hook from appointment_strategy string
    appointment_str = intelligence.get('appointment_strategy', '')
    hook = 'Free AI Readiness Assessment'
    if isinstance(appointment_str, str) and 'Hook:' in appointment_str:
        # Extract text after "Hook:" until the pipe "|"
        hook_start = appointment_str.find('Hook:') + 5
        hook_end = appointment_str.find('|', hook_start)
        if hook_end > hook_start:
            hook = appointment_str[hook_start:hook_end].strip()

    return {
        "lead_id": lead_id,
        "template_style": template_style,
        "subject": f"Transform {lead_data.get('company_name')}'s Operations with AI",
        "body": email_content,
        "intelligence_summary": {
            "hot_buttons": intelligence.get('hot_buttons', [])[:3],
            "talking_points": intelligence.get('talking_points', [])[:3],
            "hook": hook
        }
    }

def _generate_professional_email(lead_data: Dict, intelligence: Dict) -> str:
    """Generate professional email template"""
    company = lead_data.get('company_name', 'your company')
    industry = lead_data.get('industry', 'industry')
    hot_buttons = intelligence.get('hot_buttons', [])
    talking_points = intelligence.get('talking_points', [])

    # Extract hook from appointment_strategy string
    appointment_str = intelligence.get('appointment_strategy', '')
    hook = 'Free AI Readiness Assessment'
    if isinstance(appointment_str, str) and 'Hook:' in appointment_str:
        hook_start = appointment_str.find('Hook:') + 5
        hook_end = appointment_str.find('|', hook_start)
        if hook_end > hook_start:
            hook = appointment_str[hook_start:hook_end].strip()

    email = f"""Subject: Transform {company}'s Operations with AI

Dear Decision Maker,

I hope this email finds you well. I'm reaching out from LeniLani Consulting, Hawaii's leading AI and digital transformation firm.

Based on my research of {company}, I've identified several opportunities where we could drive significant value:

{chr(10).join(f'• {point}' for point in hot_buttons[:3])}

At LeniLani, we specialize in helping Hawaii {industry} companies leverage AI and data analytics to:

{chr(10).join(f'✓ {point}' for point in talking_points[:3])}

**Special Offer for {company}:**
{hook}

I'd love to schedule a brief 30-minute consultation at our Honolulu office (1050 Queen Street, Suite 100) to discuss how we can support {company}'s growth objectives.

Would you be available for a meeting next week? I have openings on Tuesday at 9 AM or Thursday at 2 PM HST.

Looking forward to connecting.

Mahalo,
LeniLani Consulting Team
1050 Queen Street, Suite 100
Honolulu, HI 96814
808-XXX-XXXX
www.lenilani.com
"""
    return email

def _generate_casual_email(lead_data: Dict, intelligence: Dict) -> str:
    """Generate casual email template"""
    company = lead_data.get('company_name', 'your company')
    hot_buttons = intelligence.get('hot_buttons', [])

    # Extract hook from appointment_strategy string
    appointment_str = intelligence.get('appointment_strategy', '')
    hook = 'free consultation'
    if isinstance(appointment_str, str) and 'Hook:' in appointment_str:
        hook_start = appointment_str.find('Hook:') + 5
        hook_end = appointment_str.find('|', hook_start)
        if hook_end > hook_start:
            hook = appointment_str[hook_start:hook_end].strip()

    email = f"""Subject: Quick question about {company}'s tech stack

Aloha!

I've been following {company} and love what you're doing. Quick question - are you looking to:

{chr(10).join(f'• {point}?' for point in hot_buttons[:2])}

We're LeniLani Consulting, based right here in Honolulu, and we help local businesses level up with AI and analytics.

Here's the deal: {hook.lower()}

Want to grab coffee at our Queen Street office and chat? No pressure, just exploring if there's a fit.

Let me know if you're free next week!

Mahalo,
The LeniLani Team
"""
    return email

def _generate_consultative_email(lead_data: Dict, intelligence: Dict) -> str:
    """Generate consultative email template"""
    company = lead_data.get('company_name', 'your company')
    industry = lead_data.get('industry', 'industry')
    talking_points = intelligence.get('talking_points', [])

    # Extract budget from budget string
    budget_str = intelligence.get('budget', '')
    budget_range = '$15,000 - $50,000'
    if isinstance(budget_str, str) and '$' in budget_str:
        # Extract budget range from string (e.g., "Budget: $15,000 - $50,000 | ...")
        if 'Budget:' in budget_str:
            budget_start = budget_str.find('Budget:') + 7
            budget_end = budget_str.find('|', budget_start)
            if budget_end > budget_start:
                budget_range = budget_str[budget_start:budget_end].strip()
        else:
            # If no "Budget:" prefix, just extract the first dollar amount pattern
            import re
            match = re.search(r'\$[\d,]+\s*-\s*\$[\d,]+', budget_str)
            if match:
                budget_range = match.group(0)

    email = f"""Subject: Strategic Technology Roadmap for {company}

Aloha,

As Hawaii's premier technology consulting firm, we've been tracking innovations in the {industry} sector, and {company} caught our attention.

**What We've Observed:**
Companies similar to {company} that have partnered with us have seen:

{chr(10).join(f'• {point}' for point in talking_points[:4])}

**Our Recommended Approach:**
Based on {company}'s profile, we suggest a phased engagement:

Phase 1: Discovery & Assessment (Complimentary)
- AI readiness evaluation
- Technology stack analysis
- ROI projection modeling

Phase 2: Implementation (Investment: {budget_range})
- Custom solution development
- Team training
- Ongoing optimization

**Next Step:**
I'd like to propose an executive briefing at our Honolulu headquarters (1050 Queen Street, Suite 100). This 45-minute session will provide you with:
- Competitive analysis specific to your market
- Technology roadmap tailored to {company}
- Clear ROI projections

Are you available for a conversation next Tuesday or Thursday?

Best regards,
LeniLani Consulting
Senior Technology Advisor
"""
    return email

@app.post("/api/campaigns/create")
async def create_campaign(campaign: Campaign):
    """Create an outreach campaign"""
    campaign_dict = campaign.dict()
    campaign_dict['id'] = f"camp_{len(in_memory_db['campaigns']) + 1}"
    campaign_dict['created_at'] = datetime.now().isoformat()

    if db:
        try:
            db.collection('campaigns').add(campaign_dict)
        except Exception as e:
            print(f"Error saving to Firebase: {e}")
            in_memory_db['campaigns'].append(campaign_dict)
    else:
        in_memory_db['campaigns'].append(campaign_dict)

    return {"message": "Campaign created", "campaign": campaign_dict}

@app.post("/api/outreach/generate")
async def generate_outreach(lead_id: str, channel: str):
    """Generate personalized outreach content"""
    # Get lead data
    lead_data = None

    if db:
        try:
            leads = db.collection('leads').where('id', '==', lead_id).stream()
            for doc in leads:
                lead_data = doc.to_dict()
                break
        except Exception as e:
            print(f"Error fetching from Firebase: {e}")

    if not lead_data:
        # Try in-memory
        for lead in in_memory_db['leads']:
            if lead.get('id') == lead_id:
                lead_data = lead
                break

    if not lead_data:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead = Lead(**lead_data)

    if channel == "email":
        content = await outreach_generator.generate_email(lead)
    elif channel == "sms":
        content = await outreach_generator.generate_sms(lead)
    elif channel == "linkedin":
        content = await outreach_generator.generate_linkedin_message(lead)
    else:
        raise HTTPException(status_code=400, detail="Invalid channel")

    return {"content": content, "channel": channel, "lead": lead_data}

@app.post("/api/outreach/send")
async def send_outreach(lead_id: str, channel: str, content: str):
    """Send outreach message"""
    # Get lead data
    lead_data = None

    if db:
        try:
            leads = db.collection('leads').where('id', '==', lead_id).stream()
            for doc in leads:
                lead_data = doc.to_dict()
                break
        except Exception as e:
            print(f"Error fetching from Firebase: {e}")

    if not lead_data:
        for lead in in_memory_db['leads']:
            if lead.get('id') == lead_id:
                lead_data = lead
                break

    if not lead_data:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead = Lead(**lead_data)

    sent = False
    if channel == "email" and sendgrid_client:
        try:
            message = Mail(
                from_email='hello@lenilani.com',
                to_emails=lead.contact_email,
                subject='Transform Your Business with AI - LeniLani Consulting',
                html_content=content.replace('\n', '<br>')
            )
            response = sendgrid_client.send(message)
            sent = True
        except Exception as e:
            print(f"Error sending email: {e}")
    elif channel == "sms" and twilio_client:
        try:
            message = twilio_client.messages.create(
                body=content,
                from_=os.getenv('TWILIO_PHONE_NUMBER'),
                to=lead.contact_phone
            )
            sent = True
        except Exception as e:
            print(f"Error sending SMS: {e}")

    # Log outreach
    log_entry = {
        'lead_id': lead_id,
        'channel': channel,
        'content': content,
        'sent_at': datetime.now().isoformat(),
        'sent': sent
    }

    if db:
        try:
            db.collection('outreach_log').add(log_entry)
        except Exception as e:
            print(f"Error logging to Firebase: {e}")
            in_memory_db['outreach_log'].append(log_entry)
    else:
        in_memory_db['outreach_log'].append(log_entry)

    return {
        "message": "Outreach sent successfully" if sent else "Outreach logged (service not configured)",
        "sent": sent
    }

@app.get("/api/appointments/slots")
async def get_available_slots():
    """Get available appointment slots"""
    slots = await scheduler.find_available_slots()
    return {"slots": slots}

@app.post("/api/appointments/book")
async def book_appointment(lead_id: str, date_time: str):
    """Book an appointment"""
    appointment = await scheduler.book_appointment(lead_id, date_time)
    return {"appointment": appointment.dict(), "message": "Appointment booked successfully"}

@app.get("/api/appointments")
async def get_appointments():
    """Get all appointments"""
    appointments = []

    if db:
        try:
            appointments = [doc.to_dict() for doc in db.collection('appointments').stream()]
        except Exception as e:
            print(f"Error fetching from Firebase: {e}")
            appointments = in_memory_db['appointments']
    else:
        appointments = in_memory_db['appointments']

    return appointments

@app.get("/api/analytics/dashboard")
async def get_analytics():
    """Get analytics dashboard data"""
    # Try Supabase analytics first
    analytics = await supabase_db.get_analytics()

    # If Supabase is available and has data, use it
    if analytics and analytics.get('total_leads', 0) > 0:
        return {
            "total_leads": analytics['total_leads'],
            "qualified_leads": analytics['qualified_leads'],
            "appointments_booked": analytics['total_appointments'],
            "conversion_rate": (analytics['total_appointments'] / analytics['total_leads']) if analytics['total_leads'] > 0 else 0,
            "revenue_potential": analytics['qualified_leads'] * 15000,  # Avg deal size
            "avg_lead_score": analytics.get('avg_lead_score', 0)
        }

    # Fallback to in-memory
    leads = in_memory_db['leads']
    appointments = in_memory_db['appointments']

    leads_count = len(leads)
    qualified_leads = len([l for l in leads if l.get('score', 0) >= 70])
    appointments_count = len(appointments)

    return {
        "total_leads": leads_count,
        "qualified_leads": qualified_leads,
        "appointments_booked": appointments_count,
        "conversion_rate": (appointments_count / leads_count) if leads_count > 0 else 0,
        "revenue_potential": qualified_leads * 15000  # Avg deal size
    }

# ============= CAMPAIGN ENDPOINTS =============

@app.post("/api/campaigns")
async def create_campaign(
    name: str,
    description: str = "",
    target_industry: str = None,
    min_score: int = 0,
    max_score: int = 100,
    channels: List[str] = ["email"]
):
    """Create a new campaign"""
    # Build target filters
    target_filters = {}
    if target_industry:
        target_filters['industry'] = target_industry
    if min_score > 0 or max_score < 100:
        target_filters['min_score'] = min_score
        target_filters['max_score'] = max_score

    campaign_data = {
        'name': name,
        'description': description,
        'target_filters': target_filters,
        'channels': channels,
        'status': 'draft'
    }

    campaign = await supabase_db.create_campaign(campaign_data)

    if not campaign:
        raise HTTPException(status_code=500, detail="Failed to create campaign")

    return campaign


@app.get("/api/campaigns")
async def get_campaigns(status: str = None):
    """Get all campaigns"""
    campaigns = await supabase_db.get_campaigns(status=status)
    return campaigns


@app.get("/api/campaigns/{campaign_id}")
async def get_campaign(campaign_id: int):
    """Get campaign by ID with analytics"""
    campaign = await supabase_db.get_campaign_by_id(campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Get analytics
    analytics = await supabase_db.get_campaign_analytics(campaign_id)

    # Get sequences
    sequences = await supabase_db.get_campaign_sequences(campaign_id)

    return {
        **campaign,
        'analytics': analytics,
        'sequences': sequences
    }


@app.put("/api/campaigns/{campaign_id}")
async def update_campaign(campaign_id: int, update_data: Dict):
    """Update campaign"""
    campaign = await supabase_db.update_campaign(campaign_id, update_data)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return campaign


@app.delete("/api/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: int):
    """Delete campaign"""
    success = await supabase_db.delete_campaign(campaign_id)

    if not success:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return {"message": "Campaign deleted successfully"}


@app.post("/api/campaigns/{campaign_id}/leads")
async def add_leads_to_campaign(campaign_id: int, lead_ids: List[str]):
    """Add leads to campaign"""
    # Verify campaign exists
    campaign = await supabase_db.get_campaign_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    success = await supabase_db.add_leads_to_campaign(campaign_id, lead_ids)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to add leads to campaign")

    return {"message": f"Added {len(lead_ids)} leads to campaign"}


@app.get("/api/campaigns/{campaign_id}/leads")
async def get_campaign_leads(campaign_id: int):
    """Get all leads in a campaign"""
    leads = await supabase_db.get_campaign_leads(campaign_id)
    return leads


@app.post("/api/campaigns/{campaign_id}/generate-sequences")
async def generate_campaign_sequences(campaign_id: int):
    """Generate AI-powered campaign sequences"""
    campaign = await supabase_db.get_campaign_by_id(campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Get LeniLani context
    lenilani_context = lenilani_content.get_context_string() if lenilani_content.content.get('loaded') else ""

    # Generate sequences using Claude
    try:
        prompt = f"""Create a 3-step outreach sequence for this campaign:

Campaign: {campaign['name']}
Description: {campaign.get('description', '')}
Target: {campaign.get('target_filters', {})}
Channels: {campaign.get('channels', ['email'])}

{lenilani_context}

Generate 3 outreach messages:
1. Initial outreach (Day 0)
2. First follow-up (Day 3)
3. Final follow-up (Day 7)

For each message, provide:
- Subject line (for email)
- Body content (personalized, consultative tone)
- CTA (call-to-action)

Focus on the specific value LeniLani can provide based on the campaign target.

Return as JSON array with format:
[
  {{
    "sequence_number": 1,
    "channel": "email",
    "delay_days": 0,
    "subject": "...",
    "content": "...",
    "template_style": "consultative"
  }},
  ...
]"""

        result = claude.invoke(prompt)

        # Extract JSON from response
        import json
        import re

        json_match = re.search(r'\[[\s\S]*\]', result.content)
        if json_match:
            sequences_data = json.loads(json_match.group(0))

            # Save sequences to database
            for seq_data in sequences_data:
                seq_data['campaign_id'] = campaign_id
                await supabase_db.create_campaign_sequence(seq_data)

            return {
                "message": "Generated campaign sequences",
                "sequences": sequences_data
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to parse AI response")

    except Exception as e:
        print(f"Error generating sequences: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate sequences: {str(e)}")


@app.post("/api/campaigns/{campaign_id}/start")
async def start_campaign(campaign_id: int):
    """Start a campaign (change status to active)"""
    campaign = await supabase_db.update_campaign(campaign_id, {
        'status': 'active',
        'started_at': datetime.utcnow().isoformat()
    })

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return campaign


@app.post("/api/campaigns/{campaign_id}/pause")
async def pause_campaign(campaign_id: int):
    """Pause a campaign"""
    campaign = await supabase_db.update_campaign(campaign_id, {
        'status': 'paused'
    })

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return campaign


# ============= APPOINTMENTS ENDPOINTS =============

@app.post("/api/appointments")
async def create_appointment(
    lead_id: str,
    date_time: str,
    location: str = "1050 Queen Street, Suite 100, Honolulu, HI 96814",
    format: str = "in-person",
    notes: str = ""
):
    """Create a new appointment"""
    appointment_data = {
        'lead_id': lead_id,
        'date_time': date_time,
        'location': location,
        'format': format,
        'status': 'scheduled',
        'notes': notes
    }

    appointment = await supabase_db.create_appointment(appointment_data)

    if not appointment:
        raise HTTPException(status_code=500, detail="Failed to create appointment")

    return appointment


@app.get("/api/appointments")
async def get_appointments(lead_id: str = None):
    """Get all appointments, optionally filtered by lead_id"""
    appointments = await supabase_db.get_appointments(lead_id)

    # Enrich appointments with lead data
    enriched_appointments = []
    for apt in appointments:
        lead = await supabase_db.get_lead_by_id(apt['lead_id'])
        enriched_appointment = {
            **apt,
            'lead': lead
        }
        enriched_appointments.append(enriched_appointment)

    return enriched_appointments


@app.put("/api/appointments/{appointment_id}")
async def update_appointment(
    appointment_id: int,
    status: str = None,
    notes: str = None,
    date_time: str = None
):
    """Update an appointment"""
    update_data = {}
    if status:
        update_data['status'] = status
    if notes is not None:
        update_data['notes'] = notes
    if date_time:
        update_data['date_time'] = date_time

    # Use Supabase client directly since we don't have update_appointment in database.py
    if not supabase_db.client:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        response = supabase_db.client.table('appointments').update(update_data).eq('id', appointment_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return response.data[0]
    except Exception as e:
        print(f"Error updating appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to update appointment")


@app.delete("/api/appointments/{appointment_id}")
async def delete_appointment(appointment_id: int):
    """Delete an appointment"""
    if not supabase_db.client:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        supabase_db.client.table('appointments').delete().eq('id', appointment_id).execute()
        return {"message": "Appointment deleted successfully"}
    except Exception as e:
        print(f"Error deleting appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete appointment")


# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
