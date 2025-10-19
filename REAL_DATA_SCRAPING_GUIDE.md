# Real Data Scraping Guide

This guide explains how to enable and configure real lead discovery from multiple sources including LinkedIn, Google, Pacific Business News, and Hawaii business directories.

## Overview

The platform now scrapes real Hawaii business data from:

✓ **LinkedIn** - Company profiles and business listings
✓ **Google Business/Maps** - Local business information with reviews and ratings
✓ **Pacific Business News** - Hawaii business news and company features
✓ **Honolulu Chamber of Commerce** - Member directory
✓ **HTDC** (Hawaii Technology Development Corporation) - Tech startup portfolio
✓ **Hawaii Business Magazine** - Business directory listings

## Quick Start

### 1. Enable Real Data Scraping

Edit `backend/.env`:

```bash
USE_REAL_DATA=true  # Enable real scraping (default: true)
```

### 2. Configure API Keys (Optional but Recommended)

For best results, add these API keys to `backend/.env`:

```bash
# For Google Maps/Business scraping (HIGHLY RECOMMENDED)
SERPAPI_KEY=your_serpapi_key_here

# For LinkedIn API access (OPTIONAL)
LINKEDIN_API_KEY=your_linkedin_key_here
```

### 3. Restart Backend

```bash
cd backend
./venv/bin/python main.py
```

You should see:
```
🚀 Real lead discovery enabled - will scrape from LinkedIn, Google, Pacific Business News, and Hawaii directories
```

## API Keys Setup

### SerpAPI (Recommended for Google Scraping)

**What it does:** Scrapes Google Maps and Google Business listings with detailed information

**How to get it:**
1. Visit https://serpapi.com/
2. Sign up for free account (100 free searches/month)
3. Go to dashboard → API Key
4. Copy your API key
5. Add to `.env`: `SERPAPI_KEY=your_key_here`

**Pricing:**
- Free tier: 100 searches/month
- Paid plans start at $50/month for 5,000 searches

### LinkedIn API (Optional)

**What it does:** Access LinkedIn company data via official API

**How to get it:**
1. Apply for LinkedIn API access at https://developer.linkedin.com/
2. Note: LinkedIn API access requires approval and partnership
3. For individuals, consider these alternatives:
   - **Phantombuster** (https://phantombuster.com/) - LinkedIn scrapers
   - **Apify** (https://apify.com/) - LinkedIn actors
   - **RapidAPI LinkedIn endpoints** (https://rapidapi.com/)

**Alternative (Without LinkedIn API):**
The system will still work without LinkedIn credentials by using:
- Public LinkedIn company page scraping (limited)
- Alternative business directories
- Google search results for companies

## Data Sources Explained

### 1. LinkedIn Scraping

**Without API key:**
- Searches public LinkedIn company pages
- Limited to publicly available data
- Respectful rate limiting

**With API key:**
- Full company profiles
- Employee counts
- Industry classifications
- Recent updates and posts

**Data collected:**
- Company name
- Website
- Industry
- Employee count
- Location
- Description
- LinkedIn URL

### 2. Google Business/Maps

**Requires:** SERPAPI_KEY (recommended)

**Data collected:**
- Business name
- Address and location coordinates
- Phone number
- Website
- Rating and review count
- Business hours
- Category/industry
- Photos

**Benefits:**
- Highly accurate local data
- Real-time information
- Customer reviews indicate business size/success
- Contact information readily available

### 3. Pacific Business News (bizjournals.com/pacific)

**No API key required**

**Data collected:**
- Company mentions in news articles
- Hawaii business features
- Industry news
- Company announcements

**Sections scraped:**
- Technology news
- Healthcare news
- Tourism & Hospitality
- Retail
- Company profiles

### 4. Hawaii Business Directories

**No API key required**

**Sources:**
- **Honolulu Chamber of Commerce** - Local business members
- **HTDC** - Technology startups and innovators
- **Hawaii Business Magazine** - General business directory

**Data collected:**
- Company names
- Basic contact information
- Industry categories
- Member status

## How Lead Discovery Works

### Workflow

1. **User clicks "Discover New Leads"** in dashboard
2. **System initiates parallel scraping:**
   - LinkedIn search for Hawaii companies
   - Google Maps search for local businesses
   - Pacific Business News article scraping
   - Hawaii directory scraping
3. **Data enrichment:**
   - Deduplicates companies
   - Estimates employee counts
   - Identifies pain points
   - Assigns initial scores
4. **AI scoring:**
   - LangChain agents score each lead
   - Industry fit analysis
   - Location priority
   - Company size evaluation
5. **Display results:**
   - Leads shown in dashboard
   - Sorted by score
   - Ready for outreach

### Customizing Search

#### Filter by Industry

Frontend (coming soon) or API:

```bash
POST /api/leads/discover
{
  "industry": "tourism",
  "max_leads": 50
}
```

Supported industries:
- tourism
- hospitality
- healthcare
- technology
- retail
- food & beverage
- professional services

#### Adjust Lead Limits

```python
# In backend/main.py
max_leads = 100  # Default is 50
```

## Performance Considerations

### Scraping Speed

- **LinkedIn:** ~2-3 seconds per company (with rate limiting)
- **Google Maps:** ~1 second per search (with SerpAPI)
- **PBN:** ~3-5 seconds per section
- **Directories:** ~5-10 seconds total

**Total time for 50 leads:** ~1-2 minutes

### Rate Limiting

All scrapers implement respectful rate limiting:
- Delays between requests
- User-agent headers
- Robots.txt compliance

### Error Handling

If any scraper fails:
- System continues with other sources
- Falls back to demo data if all fail
- Logs errors for debugging

## Compliance & Ethics

### Legal Considerations

✓ **Public data only** - We scrape publicly available information
✓ **Robots.txt compliance** - Respects website scraping rules
✓ **Rate limiting** - Prevents server overload
✓ **Attribution** - Links back to original sources

### Best Practices

1. **Use official APIs when available** (e.g., SerpAPI for Google)
2. **Don't abuse scrapers** - Limit requests, use delays
3. **Store data responsibly** - Follow privacy regulations
4. **Verify information** - Scraped data may need manual review
5. **Respect opt-outs** - Remove companies that request it

### Terms of Service

- **LinkedIn:** Review LinkedIn's User Agreement
- **Google:** Use official APIs (SerpAPI) rather than direct scraping
- **News sites:** Fair use for business research purposes
- **Directories:** Public member listings

## Troubleshooting

### No leads found

**Check:**
1. Is `USE_REAL_DATA=true` in `.env`?
2. Is backend showing "Real lead discovery enabled" message?
3. Check backend logs for errors
4. Verify internet connection
5. Try setting `USE_REAL_DATA=false` to test with demo data

### SerpAPI errors

**Solutions:**
- Verify API key is correct
- Check monthly quota (100 free searches)
- Ensure billing is enabled for paid plans
- Review SerpAPI dashboard for errors

### Rate limiting issues

**Solutions:**
- Reduce `max_leads` parameter
- Add delays in `lead_scrapers.py`
- Use official APIs instead of web scraping
- Distribute requests over time

### Empty or incomplete data

**Normal behavior:**
- Not all sources return complete information
- System enriches data with estimates
- AI analysis fills in gaps
- Manual review recommended

## Advanced Configuration

### Custom Scrapers

Add your own data sources in `backend/lead_scrapers.py`:

```python
class CustomScraper:
    async def scrape_companies(self) -> List[Dict]:
        # Your custom scraping logic
        return leads
```

Then add to orchestrator:

```python
# In RealLeadDiscoveryOrchestrator
self.custom_scraper = CustomScraper()
```

### Modify Search Queries

Edit `lead_scrapers.py`:

```python
# LinkedIn queries
search_queries = [
    "your custom query",
    "another search term"
]

# Google Maps queries
queries = [
    "specific business type",
    "industry keyword"
]
```

### Data Enrichment

Customize `_estimate_employee_count()` and other enrichment methods in `main.py` to improve lead quality.

## Support

For issues:
1. Check backend logs: Look for error messages
2. Verify API keys in `.env`
3. Test with `USE_REAL_DATA=false` first
4. Review API usage dashboards
5. Check this guide and README.md

## Future Enhancements

Planned features:
- [ ] Yelp business scraping
- [ ] Facebook business pages
- [ ] Better Business Bureau (BBB) data
- [ ] State business registrations
- [ ] Industry-specific databases
- [ ] AI-powered contact finding
- [ ] Email verification
- [ ] Company size estimation improvements
- [ ] Automated data quality scoring

---

**Ready to discover real Hawaii business leads!** 🚀🌺
