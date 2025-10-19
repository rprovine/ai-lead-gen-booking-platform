# Quick Start Guide - LeniLani Lead Generation Platform

## You're Ready to Go! 🚀

Your AI-powered lead generation platform is **fully operational** and ready to discover real Hawaii business leads.

---

## Current Status

✅ **Backend API:** Running on http://localhost:8000
✅ **Frontend Dashboard:** Running on http://localhost:3002
✅ **Real Data Scraping:** ENABLED
✅ **SerpAPI:** Configured for Google Maps/Business data
✅ **AI Models:** Claude, Gemini, OpenAI all active
✅ **Storage:** In-memory (works perfectly for current use)

---

## How to Use the Platform

### 1. Access the Dashboard

Open your browser to: **http://localhost:3002**

You'll see:
- Analytics cards showing lead metrics
- Lead pipeline with scoring
- Campaign management
- AI insights

### 2. Discover Real Hawaii Business Leads

**Click the "Discover New Leads" button**

The system will scrape from:
- **LinkedIn** - Hawaii company profiles
- **Google Business/Maps** - Local businesses with ratings, reviews, contacts
- **Pacific Business News** - Hawaii business news and features
- **Honolulu Chamber of Commerce** - Member directory
- **HTDC** - Hawaii tech startups
- **Hawaii Business Magazine** - Business listings

**What you'll get:**
- Company name
- Website & contact info
- Location & industry
- Employee count estimates
- AI-generated lead score (0-100)
- Identified pain points

### 3. Review and Score Leads

Leads are automatically scored based on:
- Industry fit (Tourism, Healthcare, Tech = higher scores)
- Location (Honolulu/Oahu preferred)
- Company size (larger = better fit)
- Digital maturity (gaps = opportunities)

**Qualified leads** have scores ≥ 70

### 4. Generate Personalized Outreach

For each lead, you can:

**📧 Email:**
- Click the email icon
- AI generates personalized email based on:
  - Company's industry
  - Identified pain points
  - Your services (AI/Chatbots, Data Analytics, Fractional CTO, Digital Marketing)
- Edit if needed
- Send via SendGrid (if configured) or copy/paste

**📱 SMS:**
- Click the SMS icon
- AI generates concise text message
- Send via Twilio (if configured) or manually

**💼 LinkedIn:**
- Generate connection message
- Personalized to their business needs

### 5. Book Appointments

**Click "Book Meeting"** on qualified leads

The system:
- Finds available time slots
- Creates calendar event
- Books at your Honolulu office: **1050 Queen Street, Suite 100**
- Can do in-person or virtual meetings

### 6. Monitor Analytics

Dashboard shows real-time metrics:
- **Total Leads** - All discovered businesses
- **Qualified Leads** - Score ≥ 70
- **Appointments** - Meetings scheduled
- **Conversion Rate** - Success percentage
- **Revenue Potential** - Estimated value (qualified leads × $15K avg)

---

## API Documentation

For developers: **http://localhost:8000/docs**

Interactive Swagger UI with all endpoints:
- `POST /api/leads/discover` - Discover new leads
- `GET /api/leads` - Get all leads
- `POST /api/leads/score` - Score a lead
- `POST /api/outreach/generate` - Generate personalized messages
- `POST /api/outreach/send` - Send outreach
- `POST /api/appointments/book` - Book meetings
- `GET /api/analytics/dashboard` - Get metrics

---

## Data Sources & Scraping

### What Gets Scraped

**LinkedIn:**
- Company profiles
- Industry classifications
- Employee counts
- Business descriptions

**Google Business/Maps** (via SerpAPI):
- Business name, address, phone
- Website URLs
- Customer ratings & reviews
- Business hours
- GPS coordinates

**Pacific Business News:**
- Hawaii business news
- Company announcements
- Industry features

**Hawaii Directories:**
- Chamber of Commerce members
- HTDC tech portfolio
- Hawaii Business Magazine listings

### Scraping Configuration

**Current Settings:**
```bash
USE_REAL_DATA=true  # Real scraping enabled
SERPAPI_KEY=configured  # Google Maps access
```

**To toggle demo mode:**
Edit `backend/.env` and set `USE_REAL_DATA=false`

---

## Tips for Best Results

### Lead Discovery

1. **Start broad** - Let the system discover from all sources
2. **Use filters** - Focus on specific industries if needed
3. **Review scores** - Prioritize leads with 70+ scores
4. **Check pain points** - AI identifies opportunities automatically

### Outreach Strategy

1. **Personalize** - Edit AI-generated content to add personal touches
2. **Reference specifics** - Mention their industry, location, or news
3. **Lead with value** - Focus on solving their problems
4. **Multi-channel** - Combine email + LinkedIn for best results

### Lead Qualification

**High-value indicators:**
- Tourism/Hospitality industry
- 100+ employees
- Honolulu/Oahu location
- Multiple pain points identified
- Poor digital maturity score

**Services to offer:**
- AI Chatbot Development
- Data Analytics & BI Dashboards
- Fractional CTO Services
- HubSpot/Digital Marketing

---

## Customization Options

### Target Different Industries

Currently optimized for:
- Tourism & Hospitality
- Healthcare
- Technology
- Professional Services
- Retail
- Food & Beverage

**To add more:** Edit search queries in `backend/lead_scrapers.py`

### Adjust Lead Scoring

Edit `backend/main.py` - `LeadScoringAgent` class:
- Change industry weights
- Adjust location preferences
- Modify company size importance

### Customize Outreach Templates

Edit `backend/main.py` - `OutreachGenerator` class:
- Change tone/style
- Adjust value propositions
- Modify call-to-action language

---

## Troubleshooting

### No leads appearing?

**Check:**
1. Backend logs for errors: Look at terminal running backend
2. `USE_REAL_DATA=true` in `backend/.env`
3. Internet connection (for web scraping)
4. SerpAPI quota (100 free searches/month)

**Quick fix:**
```bash
# Set to demo mode temporarily
# Edit backend/.env
USE_REAL_DATA=false
```

### Outreach not generating?

**Required:** At least one AI API key (Claude, Gemini, or OpenAI)

**Check:** `backend/.env` has valid API keys

### Can't book appointments?

**Calendar integration** requires Google Calendar API (optional)

For now, appointments are logged in the system - you can manually add to calendar.

---

## Storing Data

### Current: In-Memory Storage

**Pros:**
- ✅ Fast and simple
- ✅ No setup required
- ✅ Works immediately

**Cons:**
- ❌ Leads lost on backend restart
- ❌ No cloud backup

### Export Leads (Recommended)

To save your discovered leads:
1. Use the dashboard to review leads
2. Copy data you want to keep
3. Or use API: `GET /api/leads` returns JSON

### Future: Persistent Storage

When ready, you can add:
- **PostgreSQL** - Local database
- **Supabase** - Hosted PostgreSQL
- **MongoDB** - NoSQL option

Firebase is not available due to organization policy restrictions.

---

## Next Steps

### Immediate Actions

1. ✅ **Test Lead Discovery**
   - Go to http://localhost:3002
   - Click "Discover New Leads"
   - Watch real Hawaii businesses populate

2. ✅ **Generate Outreach**
   - Pick a high-scoring lead
   - Click email/SMS icons
   - Review AI-generated content

3. ✅ **Book Demo Meeting**
   - Try booking an appointment
   - See available time slots

### Coming Soon

- Export leads to CSV/Excel
- Email templates library
- Automated follow-up sequences
- Advanced analytics with charts
- A/B testing for outreach
- LinkedIn automation
- Mobile app

---

## Support & Resources

**Documentation:**
- `README.md` - Complete platform overview
- `REAL_DATA_SCRAPING_GUIDE.md` - Detailed scraping docs
- `API_KEYS_GUIDE.md` - API setup instructions

**API Keys:**
- SerpAPI: https://serpapi.com/
- Anthropic Claude: https://console.anthropic.com/
- Google Gemini: https://makersuite.google.com/
- OpenAI: https://platform.openai.com/

**Questions?**
Check backend logs and API documentation at http://localhost:8000/docs

---

## Platform Architecture

```
┌─────────────────────────────────────────┐
│   Frontend (Next.js) :3002              │
│   - Dashboard UI                         │
│   - Lead Pipeline                        │
│   - Outreach Generator                   │
│   - Analytics View                       │
└─────────────────────────────────────────┘
                  ↕ HTTP
┌─────────────────────────────────────────┐
│   Backend (FastAPI) :8000               │
│   - Lead Discovery Service               │
│   - AI Scoring Agents                    │
│   - Outreach Generator                   │
│   - Appointment Scheduler                │
└─────────────────────────────────────────┘
                  ↕
┌─────────────────────────────────────────┐
│   Real Data Scrapers                    │
│   ├─ LinkedIn Scraper                   │
│   ├─ Google Maps (SerpAPI)              │
│   ├─ Pacific Business News              │
│   └─ Hawaii Directories                 │
└─────────────────────────────────────────┘
                  ↕
┌─────────────────────────────────────────┐
│   AI Services                           │
│   ├─ Claude (Anthropic)                 │
│   ├─ Gemini (Google)                    │
│   └─ OpenAI                             │
└─────────────────────────────────────────┘
```

---

## Your LeniLani Office

**Address:** 1050 Queen Street, Suite 100, Honolulu, HI 96814

All appointments are automatically configured for this location.

---

**Ready to generate real Hawaii business leads!** 🌺🚀

Visit http://localhost:3002 and click "Discover New Leads" to get started!
