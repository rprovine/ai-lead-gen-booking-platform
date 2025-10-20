# LeniLani Lead Generation & Appointment Booking Platform

AI-powered lead discovery, qualification, and appointment booking system for LeniLani Consulting, specializing in Hawaii-based businesses.

## Features

### Lead Discovery & Enrichment
- **Smart Query Rotation**: Intelligent search query rotation system that cycles through multiple variations to discover diverse leads
- **Automated Lead Discovery**: AI-powered web scraping to find Hawaii businesses needing tech services
- **ICP Management**: Define and manage your Ideal Customer Profile with smart targeting
- **Lead Enrichment Pipeline**: Automated workflow to enrich leads with Perplexity research and AI-generated playbooks
- **Intelligent Lead Scoring**: LangChain agents score leads based on multiple factors
- **Lead Status Tracking**: Track leads through NEW → RESEARCHED → IN_HUBSPOT lifecycle

### AI-Powered Intelligence
- **Perplexity AI Research**: Real-time company intelligence from the past 90 days (news, leadership, market position)
- **Enhanced Contact Finding**: Multi-source decision maker discovery using Apollo.io, Hunter.io, Perplexity AI, and Google Search
- **PDF Sales Playbooks**: Professional downloadable playbooks with AI insights and Perplexity research
- **AI Insights**: Claude-powered sales intelligence with actionable recommendations

### Outreach & CRM
- **Smart Email Templates**: Auto-generated emails in professional, casual, or consultative styles
- **Personalized Outreach**: Generate custom emails, SMS, and LinkedIn messages using Claude/Gemini
- **Smart Appointment Booking**: Automated scheduling at your Honolulu office (1050 Queen Street, Suite 100)
- **Multi-Channel Campaigns**: Email, SMS, and LinkedIn outreach orchestration
- **HubSpot Integration**: Automatic CRM synchronization with leads, contacts, companies, and formatted intelligence notes

### Analytics & Automation
- **Real-time Analytics**: Dashboard showing leads, conversions, and revenue potential
- **Automated Daily Discovery**: Cron job system for hands-free lead generation
- **Database Migration Tools**: Easy schema updates and data management

## Tech Stack

**Backend:**
- FastAPI (Python)
- LangChain (Claude 3.5 Sonnet, Gemini, OpenAI)
- Supabase (PostgreSQL)
- Perplexity AI (Sonar Pro) for research
- ReportLab for PDF generation
- Redis (optional)
- Celery for background tasks (optional)

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Framer Motion

**Integrations:**
- Anthropic Claude API (3.5 Sonnet)
- Perplexity AI (Sonar Pro - research & contact discovery)
- Google Gemini API
- OpenAI API
- SerpAPI (Google Maps/Business data)
- Google Custom Search API (Contact discovery)
- Apollo.io (Decision maker contact finder)
- Hunter.io (Email finder & verification)
- RocketReach (Executive contact data)
- HubSpot (Full CRM sync with contacts, companies, and notes)
- SendGrid (Email - optional)
- Twilio (SMS - optional)
- Google Calendar API (optional)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional)
- API keys (see [API_KEYS_GUIDE.md](./API_KEYS_GUIDE.md))

### Option 1: Local Development (Recommended for getting started)

#### 1. Clone the repository

```bash
git clone <your-repo-url>
cd ai-lead-gen-booking-platform
```

#### 2. Set up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.template .env
# Edit .env and add your API keys (see API_KEYS_GUIDE.md)

# Run the backend
python main.py
```

Backend will be available at http://localhost:8000

#### 3. Set up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
# .env.local is already created with the correct API URL

# Run the development server
npm run dev
```

Frontend will be available at http://localhost:3000

#### 4. Access the Dashboard

Open your browser to http://localhost:3000 and you'll see the LeniLani Lead Generation Platform dashboard!

### Option 2: Docker Compose (For production-like environment)

```bash
# Make sure your API keys are set in the .env file
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Configuration

### Required API Keys

**Minimum setup (to get started):**
1. ANTHROPIC_API_KEY - Get from https://console.anthropic.com/
2. GOOGLE_AI_API_KEY - Get from https://makersuite.google.com/app/apikey
3. OPENAI_API_KEY - Get from https://platform.openai.com/api-keys

**Optional (for full functionality):**
- SENDGRID_API_KEY - For email outreach
- TWILIO credentials - For SMS outreach
- HUBSPOT_API_KEY - For CRM integration
- Firebase credentials - For persistent storage

See [API_KEYS_GUIDE.md](./API_KEYS_GUIDE.md) for detailed setup instructions.

### Environment Variables

Edit `backend/.env`:

```bash
# AI/ML APIs (Required)
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_AI_API_KEY=AIza-your-key-here
OPENAI_API_KEY=sk-your-key-here

# Email (Optional)
SENDGRID_API_KEY=SG.your-key-here

# SMS (Optional)
TWILIO_ACCOUNT_SID=AC-your-sid-here
TWILIO_AUTH_TOKEN=your-token-here
TWILIO_PHONE_NUMBER=+1808XXXXXXX

# CRM (Optional)
HUBSPOT_API_KEY=pat-na1-your-key-here

# Database (Optional - uses in-memory by default)
DATABASE_URL=postgresql://postgres:password@localhost:5432/lenilani_leads
FIREBASE_SERVICE_ACCOUNT_PATH=./serviceAccountKey.json

# Office Address
OFFICE_ADDRESS=1050 Queen Street, Suite 100, Honolulu, HI 96814
```

## Usage

### 1. Discover Leads

Click the **"Discover New Leads"** button in the dashboard. The AI will:
- Use smart query rotation to search for diverse Hawaii businesses
- Analyze their websites for opportunities
- Score each lead based on multiple factors
- Find decision maker contact information from multiple sources
- Display them in your pipeline

### 2. Enrich Leads

The enrichment pipeline automatically:
- Conducts Perplexity AI research on each company
- Finds decision maker contacts (Apollo, Hunter, Perplexity, Google)
- Generates personalized PDF sales playbooks
- Creates AI-powered sales intelligence
- Updates lead status: NEW → RESEARCHED

### 3. Sync to HubSpot

Send enriched leads to HubSpot CRM:
- Creates/updates contact records for decision makers
- Creates/updates company records
- Adds formatted intelligence notes with research
- Links to downloadable PDF playbooks
- Updates lead status: RESEARCHED → IN_HUBSPOT

### 4. Generate Outreach

For each lead, you can:
- Click the email icon to generate a personalized email
- Click the SMS icon to generate a text message
- Review and edit the AI-generated content
- Send directly through the platform

### 5. Book Appointments

Click **"Book Meeting"** to schedule an appointment at your Honolulu office. The system will:
- Find available time slots
- Create a calendar event
- Send confirmations to the lead
- Add reminders

### 6. Monitor Analytics

The dashboard shows:
- Total leads discovered
- Qualified leads (score > 70)
- Appointments booked
- Conversion rate
- Revenue potential

### 7. Automated Daily Discovery (Optional)

Set up a cron job for hands-free lead generation:
```bash
# Run the setup script
cd backend
chmod +x daily_discovery.sh
./setup_hubspot.sh  # Configure HubSpot integration first

# Add to crontab for daily 9 AM runs
crontab -e
# Add: 0 9 * * * /path/to/backend/daily_discovery.sh
```

See `backend/CRON_JOB_SETUP.md` for detailed instructions.

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

**Lead Management:**
- `POST /api/leads/discover` - Discover new leads from multiple sources
- `GET /api/leads?status=NEW&min_score=70` - Get leads with filters (status, min_score)
- `POST /api/leads/score` - Score a lead
- `POST /api/leads/{lead_id}/intelligence?refresh=true` - Generate AI intelligence with Perplexity research
- `GET /api/leads/{lead_id}/playbook` - Download PDF sales playbook
- `POST /api/leads/{lead_id}/email-template?template_style=professional` - Generate email template
- `POST /api/leads/{lead_id}/send-to-hubspot` - Sync lead to HubSpot CRM

**Outreach & Campaigns:**
- `POST /api/outreach/generate` - Generate personalized outreach
- `POST /api/outreach/send` - Send outreach message
- `POST /api/campaigns` - Create outreach campaign
- `GET /api/campaigns` - Get all campaigns
- `POST /api/campaigns/{campaign_id}/leads` - Add leads to campaign
- `POST /api/campaigns/{campaign_id}/start` - Start campaign

**Appointments:**
- `GET /api/appointments/slots` - Get available appointment slots
- `POST /api/appointments/book` - Book an appointment
- `GET /api/appointments` - Get all appointments

**Analytics:**
- `GET /api/analytics/dashboard` - Get dashboard analytics
- `GET /health` - Health check endpoint

## Project Structure

```
ai-lead-gen-booking-platform/
├── backend/
│   ├── main.py                          # FastAPI application
│   ├── database.py                      # Supabase database client
│   ├── executive_finder.py              # Multi-source contact finder
│   ├── lead_enrichment_pipeline.py      # Automated enrichment workflow
│   ├── query_manager.py                 # Smart query rotation system
│   ├── icp_manager.py                   # ICP management
│   ├── requirements.txt                 # Python dependencies
│   ├── .env.template                    # Environment variables template
│   ├── migrations/                      # Database migration scripts
│   │   ├── add_decision_makers_column.sql
│   │   ├── add_hubspot_fields.sql
│   │   └── add_status_tracking.sql
│   ├── Documentation/
│   │   ├── COMPLETE_SYSTEM_SUMMARY.md   # Full system overview
│   │   ├── HOW_IT_WORKS.md              # Workflow documentation
│   │   ├── HUBSPOT_INTEGRATION.md       # HubSpot setup guide
│   │   ├── SMART_DISCOVERY_README.md    # Query rotation docs
│   │   ├── ENRICHMENT_WORKFLOW.md       # Enrichment process
│   │   ├── QUICK_REFERENCE.md           # Common commands
│   │   └── CRON_JOB_SETUP.md            # Automation setup
│   ├── Utility Scripts/
│   │   ├── setup_hubspot.sh             # HubSpot configuration
│   │   ├── daily_discovery.sh           # Cron job script
│   │   ├── enrich_researched_leads.py   # Enrichment utility
│   │   ├── apply_migration.py           # Database migrations
│   │   ├── reload_schema.py             # Schema management
│   │   ├── reset_lead_status.py         # Status reset utility
│   │   └── test_*.py                    # Testing utilities
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx                     # Main dashboard
│   │   ├── layout.tsx                   # App layout
│   │   └── globals.css                  # Global styles
│   ├── components/
│   │   └── ui/                          # shadcn/ui components
│   ├── lib/
│   │   └── utils.ts                     # Utility functions
│   ├── package.json
│   └── Dockerfile
├── infrastructure/
│   └── deploy.sh                        # Deployment script
├── docker-compose.yml
├── README.md
└── API_KEYS_GUIDE.md
```

## Deployment

### Deploy to Google Cloud Run + Vercel

```bash
# Set environment variables
export GCP_PROJECT_ID=your-project-id
export ANTHROPIC_API_KEY=your-key
export GOOGLE_AI_API_KEY=your-key
export OPENAI_API_KEY=your-key

# Run deployment script
cd infrastructure
chmod +x deploy.sh
./deploy.sh
```

This will:
1. Build and push backend to Google Cloud Run
2. Build and deploy frontend to Vercel
3. Configure environment variables
4. Return URLs for both services

## Customization

### Modify Lead Discovery Criteria

Edit `backend/main.py` in the `LeadDiscoveryService.discover_hawaii_businesses()` method to customize:
- Search queries
- Target industries
- Company size filters
- Geographic focus

### Customize Outreach Templates

Modify the prompts in `OutreachGenerator` class to adjust:
- Email tone and style
- SMS message format
- Value propositions
- Call-to-action language

### Adjust Lead Scoring

Update the `LeadScoringAgent` class to change:
- Scoring weights
- Industry priorities
- Location preferences
- Company size importance

## Troubleshooting

### Backend won't start
- Check that all required API keys are set in `.env`
- Verify Python version is 3.11+
- Try: `pip install -r requirements.txt --upgrade`

### Frontend build errors
- Delete `node_modules` and `.next` folders
- Run `npm install` again
- Check Node.js version is 20+

### API key errors
- Verify keys have no extra spaces
- Check keys are valid and not expired
- Ensure billing is enabled for paid APIs
- See [API_KEYS_GUIDE.md](./API_KEYS_GUIDE.md)

### Leads not being discovered
- Check your API rate limits
- Verify network connectivity
- Review API usage dashboards
- Check backend logs for errors

## Development

### Run tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code formatting

```bash
# Backend
black .
flake8 .

# Frontend
npm run lint
```

## Documentation

Comprehensive guides are available in the `backend/` directory:

- **[COMPLETE_SYSTEM_SUMMARY.md](backend/COMPLETE_SYSTEM_SUMMARY.md)** - Complete system architecture and workflow overview
- **[HOW_IT_WORKS.md](backend/HOW_IT_WORKS.md)** - Detailed explanation of the lead generation process
- **[HUBSPOT_INTEGRATION.md](backend/HUBSPOT_INTEGRATION.md)** - HubSpot setup and integration guide
- **[SMART_DISCOVERY_README.md](backend/SMART_DISCOVERY_README.md)** - Query rotation system documentation
- **[ENRICHMENT_WORKFLOW.md](backend/ENRICHMENT_WORKFLOW.md)** - Lead enrichment pipeline details
- **[QUICK_REFERENCE.md](backend/QUICK_REFERENCE.md)** - Common commands and workflows
- **[CRON_JOB_SETUP.md](backend/CRON_JOB_SETUP.md)** - Automated discovery setup guide
- **[QUERY_ROTATION_GUIDE.md](backend/QUERY_ROTATION_GUIDE.md)** - Smart query management
- **[SYSTEM_VS_HUBSPOT.md](backend/SYSTEM_VS_HUBSPOT.md)** - Understanding system vs HubSpot data flow

## Support

For issues, questions, or contributions:
- Check the comprehensive documentation in `backend/` folder
- Review the [API_KEYS_GUIDE.md](./API_KEYS_GUIDE.md)
- Visit FastAPI docs: http://localhost:8000/docs
- Check application logs for errors

## License

MIT License - See LICENSE file for details

## About LeniLani Consulting

This platform is built for LeniLani Consulting, a Honolulu-based technology consulting firm specializing in:
- AI/ML Solutions & Chatbot Development
- Data Analytics & Business Intelligence
- Fractional CTO Services
- Digital Marketing & HubSpot Implementation

**Office**: 1050 Queen Street, Suite 100, Honolulu, HI 96814

## Security & Privacy

- All API keys are stored locally and never shared
- Lead data is stored in your own Firebase/PostgreSQL instance
- Outreach is sent from your own SendGrid/Twilio accounts
- No data is sent to third parties except the configured APIs
- See `.gitignore` for excluded sensitive files

## Roadmap

- [ ] LinkedIn API integration for automated connection requests
- [ ] Advanced analytics with charts and graphs
- [ ] Email template library
- [ ] A/B testing for outreach campaigns
- [ ] Automated follow-up sequences
- [ ] Integration with Google Calendar for smart scheduling
- [ ] Mobile app (React Native)
- [ ] Multi-language support (Hawaiian, Japanese, Chinese)

---

Built with ❤️ in Honolulu, Hawaii
